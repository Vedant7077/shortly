
from datetime import datetime
import time
import os

import secrets
import string

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse,JSONResponse
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from database import get_read_db, get_write_db
from models import Link, OutboxEvent
from sqlalchemy import update

from prometheus_fastapi_instrumentator import Instrumentator
from redis_client import redis_client
import redis
from redis_client import redis_client, record_click

import logging

PUBLIC_BASE_URL = os.getenv(
    "PUBLIC_BASE_URL",
    "http://localhost"
).rstrip("/")


logger = logging.getLogger(__name__)
RATE_LIMIT = 100
WINDOW_SECONDS = 60

RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])

if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end

return count
"""

def check_rate_limit(client_ip: str) -> bool:
    current_window = int(time.time()) // WINDOW_SECONDS

    key = f"rate_limit:{client_ip}:{current_window}"

    count = redis_client.eval(
        RATE_LIMIT_SCRIPT,
        1,
        key,
        WINDOW_SECONDS
    )

    return count <= RATE_LIMIT

def invalidate_cache_with_retry(code: str) -> bool:
    cache_key = f"short:{code}"

    for attempt in range(1, 4):
        try:
            redis_client.delete(cache_key)

            logger.info(
                "Cache invalidated for %s on attempt %s",
                code,
                attempt,
            )
            return True

        except redis.RedisError:
            logger.exception(
                "Cache invalidation failed for %s (attempt %s)",
                code,
                attempt,
            )

            if attempt < 3:
                delay = 2 ** (attempt - 1)
                logger.info("Retrying in %s seconds", delay)
                time.sleep(delay)

    logger.error(
        "All cache invalidation attempts failed for %s",
        code,
    )

    return False


app = FastAPI(title="Shortly API")

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):

    # Prometheus scraping should not consume user quota
    if request.url.path == "/metrics":
        return await call_next(request)

    # Nginx forwards the original client IP
    forwarded_for = request.headers.get("X-Forwarded-For")

    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    try:
        allowed = check_rate_limit(client_ip)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Try again later."},
                headers={"Retry-After": "60"}
            )

    except redis.RedisError:
        logger.exception("Rate limiter unavailable; allowing request")

    return await call_next(request)

Instrumentator().instrument(app).expose(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ShortenRequest(BaseModel):
    url: HttpUrl

class UpdateLinkRequest(BaseModel):
    url: HttpUrl


@app.get("/")
def home():
    return {"message": "Welcome to Shortly API!"}


@app.post("/api/links")
def create_short_link(
    request: ShortenRequest,
    db: Session = Depends(get_write_db),
):
    characters = string.ascii_letters + string.digits

    # Generate a code that is not already in the database
    while True:
        code = "".join(
            secrets.choice(characters) for _ in range(6)
        )

        existing_link = (
            db.query(Link)
            .filter(Link.short_code == code)
            .first()
        )

        if existing_link is None:
            break

    original_url = str(request.url)

    new_link = Link(
        short_code=code,
        original_url=original_url,
    )

    db.add(new_link)
    db.commit()
    db.refresh(new_link)

    return {
    "id": new_link.id,
    "original_url": new_link.original_url,
    "short_code": new_link.short_code,
    "short_url": f"{PUBLIC_BASE_URL}/{new_link.short_code}",
    "created_at": new_link.created_at,
    "clicks": new_link.clicks,
}


@app.get("/api/links")
def get_links(db: Session = Depends(get_read_db)):
    saved_links = (
        db.query(Link)
        .order_by(Link.created_at.desc())
        .all()
    )

    return [
        {
            "id": link.id,
            "original_url": link.original_url,
            "short_code": link.short_code,
            "short_url": f"{PUBLIC_BASE_URL}/{link.short_code}",
            "created_at": link.created_at,
            "clicks": link.clicks,
        }
        for link in saved_links
    ]




@app.put("/api/links/{code}")
def update_short_link(
    code: str,
    request: UpdateLinkRequest,
    db: Session = Depends(get_write_db),
):
    try:
        # Begin one PostgreSQL transaction
        with db.begin():

            # Step 1: Find the existing link
            link = (
                db.query(Link)
                .filter(Link.short_code == code)
                .first()
            )

            if link is None:
                raise HTTPException(
                    status_code=404,
                    detail="Short link not found",
                )

            # Step 2: Update the original URL
            link.original_url = str(request.url)

            # Step 3: Create an outbox event
            event = OutboxEvent(
                event_type="CACHE_INVALIDATION",
                payload={"short_code": code},
                status="pending",
            )

            db.add(event)

        # Transaction automatically commits here.

        return {
            "message": "Short link updated successfully",
            "short_code": code,
            "original_url": str(request.url),
            "outbox_event_created": True,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception(
            "Failed to update link and create outbox event"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to update short link",
        )



@app.get("/{code}")
def redirect_to_original(
    code: str,
    db: Session = Depends(get_read_db),
):
    cache_key = f"short:{code}"

    # Step 1: Check Redis cache
    original_url = redis_client.get(cache_key)

    if original_url:
        print("CACHE HIT:", code)

    else:
        print("CACHE MISS:", code)

        # Step 2: Fetch URL from PostgreSQL
        link = (
            db.query(Link)
            .filter(Link.short_code == code)
            .first()
        )

        if link is None:
            raise HTTPException(
                status_code=404,
                detail="Short link not found",
            )

        original_url = link.original_url

        # Step 3: Store URL in Redis with a 1-hour TTL
        redis_client.setex(
            cache_key,
            3600,
            original_url,
        )

    # Step 4: Increment clicks in PostgreSQL
    record_click(code)

    # Step 5: Redirect user
    return RedirectResponse(
        url=original_url,
        status_code=307,
    )
