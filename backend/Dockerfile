
FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "if [ -n \"$DATABASE_URL_UNPOOLED\" ]; then alembic -x target=neon upgrade head || exit 1; fi; python worker.py & exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
