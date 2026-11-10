# Shortly — Scalable URL Shortener & Analytics

A URL shortening platform built to explore practical backend engineering and system design concepts, including horizontal scaling, caching, rate limiting, background processing, database optimization, and performance monitoring.

## Live Demo

**Try Shortly:** https://shortly-frontend-ten.vercel.app/

| Component | Live URL |
|---|---|
| Frontend | https://shortly-frontend-ten.vercel.app/ |
| Backend API | https://shortly-backend-63j2.onrender.com/ |
| API Documentation | https://shortly-backend-63j2.onrender.com/docs |
| API Metrics | https://shortly-backend-63j2.onrender.com/metrics |

**GitHub Repository:** https://github.com/Vedant7077/shortly

## Overview

Shortly allows users to create short URLs, redirect visitors to original destinations, and monitor link analytics through a dashboard.

The project focuses on building a backend that can handle concurrent requests efficiently while maintaining data consistency and reliability.

The application is deployed using cloud services, with a React frontend, FastAPI backend, managed PostgreSQL database, and managed Redis instance.

## Features

- **URL Shortening:** Generate unique short codes for long URLs.
- **URL Redirection:** Redirect visitors to their original destinations.
- **Click Analytics:** Track individual link visits and total clicks.
- **Live Dashboard:** Display link statistics.
- **Redis Caching:** Cache URL mappings for faster redirects.
- **Rate Limiting:** Protect API endpoints using Redis-backed rate limiting.
- **Horizontal Scaling:** Run multiple FastAPI instances behind Nginx in the local Docker environment.
- **Background Processing:** Aggregate click events asynchronously.
- **Outbox Pattern:** Reliably process URL-update events and invalidate cached mappings.
- **Database Optimization:** SQLAlchemy connection pooling and application-level read/write routing.
- **Monitoring:** Prometheus metrics and Grafana dashboards.
- **Load Balancing:** Distribute incoming API traffic between backend instances.

## System Architecture

### Production Architecture

The production application uses the following architecture:

```text
                  React + Vite
                  (Vercel)
                      |
                      v
                FastAPI Backend
                  (Render)
                      |
             +--------+--------+
             |                 |
             v                 v
       Neon PostgreSQL     Upstash Redis
          Database          Cache and
                            Rate Limiting
             ^                 |
             |                 v
             +---------- Background
                         Click Worker
```

- **Vercel:** Hosts the React frontend.
- **Render:** Hosts the FastAPI backend and background click worker.
- **Neon:** Provides managed PostgreSQL storage.
- **Upstash:** Provides managed Redis for caching, rate limiting, and click counters.

### Local Development Architecture

The local Docker Compose environment provides a more scalable infrastructure setup:

```text
                    React Frontend
                          |
                          v
                        Nginx
                          |
                 +--------+--------+
                 |                 |
                API1              API2
                 |                 |
                 +--------+--------+
                          |
                +---------+---------+
                |                   |
            PostgreSQL            Redis
                                    |
                              Click Counters
                                    |
                              Background
                                Worker
                                    |
                                    v
                              PostgreSQL
                                    |
                              Outbox Events
                                    |
                              Cache Invalidation
```

Prometheus collects application metrics from both API instances, while Grafana provides monitoring and visualization.

## Technology Stack

| Component | Technology |
|---|---|
| Frontend | React, Vite, JavaScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Production Database Hosting | Neon |
| ORM | SQLAlchemy |
| Cache and Rate Limiting | Redis |
| Production Redis Hosting | Upstash |
| Reverse Proxy | Nginx |
| Background Processing | Python Workers |
| Database Migrations | Alembic |
| Monitoring | Prometheus, Grafana |
| Load Testing | k6 |
| Containerization | Docker, Docker Compose |
| Frontend Deployment | Vercel |
| Backend Deployment | Render |

## System Design Concepts Implemented

### 1. Horizontal Scaling

Two FastAPI instances run independently behind Nginx in the local Docker environment. Requests are distributed across both instances, and API instance failure was tested locally.

### 2. Redis Caching

Frequently accessed URL mappings are cached in Redis to reduce repeated database queries.

### 3. Rate Limiting

A Redis-backed fixed-window rate limiter restricts requests per client IP. The configured limit is 100 requests per minute.

### 4. Click Aggregation

Click events are incremented atomically in Redis and periodically collected by a background worker. Aggregated batches are persisted in PostgreSQL.

### 5. Idempotent Batch Processing

Batch identifiers prevent the same click batch from being applied more than once.

### 6. Transactional Outbox Pattern

URL-update events are stored in PostgreSQL and processed asynchronously. The worker invalidates corresponding Redis cache entries and marks successfully processed events.

### 7. Database Connection Pooling

SQLAlchemy connection pools are configured separately for the two local API instances.

Application-level read/write routing is implemented using separate database sessions. Both currently connect to the same PostgreSQL instance; a physical read replica is not configured.

### 8. Monitoring and Observability

Prometheus scrapes metrics from both local API instances, and Grafana is used to visualize application performance.

## Performance Testing

Load testing was performed locally using k6.

| Metric | Earlier Baseline | Two-Instance Setup |
|---|---:|---:|
| Virtual Users | 10 | 10 |
| Test Duration | 30 seconds | 30 seconds |
| Requests per Second | ~599 | ~1,357 |
| Average Latency | 16.63 ms | 7.33 ms |
| p95 Latency | 26.76 ms | 10.16 ms |
| HTTP Failures | 0% | 0% |

The two-instance test achieved approximately **2.26× the baseline throughput**.

**Note:** These are local benchmark results from the development machine, not production capacity guarantees. Results depend on hardware, caching, and the test environment.

## Project Structure

```text
shortly/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── redis_client.py
│   ├── click_aggregator.py
│   ├── batch_processor.py
│   ├── worker.py
│   ├── outbox_worker.py
│   ├── migration/
│   │   └── versions/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic.ini
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
├── monitoring/
│   └── prometheus.yml
├── nginx/
│   └── nginx.conf
├── tests/
│   └── redirect-test.js
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Running Locally

### Prerequisites

- Docker Desktop
- Node.js and npm
- Python 3.13+ (for running Alembic commands locally)

### 1. Clone the Repository

```bash
git clone https://github.com/Vedant7077/shortly.git
cd shortly
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Update `.env` with your local database credentials and configuration.

### 3. Start the Backend Infrastructure

```bash
docker compose up -d --build
```

This starts PostgreSQL, Redis, both API instances, Nginx, the background worker, Prometheus, and Grafana.

### 4. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Open:

http://localhost:5173

### 5. Access Monitoring

- Frontend: http://localhost:5173
- API through Nginx: http://localhost
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome endpoint |
| POST | `/api/links` | Create a shortened URL |
| GET | `/api/links` | Retrieve saved links |
| PUT | `/api/links/{code}` | Update a shortened URL |
| GET | `/{code}` | Redirect to the original URL |
| GET | `/metrics` | Prometheus metrics |

## Deployment

Shortly is deployed using the following cloud services:

| Service | Platform |
|---|---|
| Frontend | Vercel |
| Backend API | Render |
| PostgreSQL Database | Neon |
| Redis | Upstash |

The backend uses environment variables for production database connections, Redis connectivity, CORS configuration, and public URL configuration.

Database migrations are executed during container startup before the FastAPI application starts.

The background click worker runs alongside the API in the deployed Render container.

**Deployment URLs:**

- Frontend: https://shortly-frontend-ten.vercel.app/
- Backend: https://shortly-backend-63j2.onrender.com/
- API Documentation: https://shortly-backend-63j2.onrender.com/docs

**Note:** The free Render instance may spin down after inactivity, resulting in a delay when the application is accessed again.

## Future Improvements

- Introduce a managed PostgreSQL read replica.
- Improve automated integration and end-to-end testing.
- Add authentication and user-specific link management.
- Add custom short codes and link expiration.
- Improve production monitoring and alerting.
- Implement more robust background worker recovery and reliability.
- Perform production load testing and capacity analysis.

## Author

**Vedant Palekar**

Computer Engineering Student | Backend Development | System Design | Cloud & AI

GitHub: https://github.com/Vedant7077

---

*Shortly is a practical system design learning project focused on understanding how scalable backend systems are designed, implemented, tested, and deployed.*