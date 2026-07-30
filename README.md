# 🌍 TerraScore AI

Climate + Drought Prediction System for Farmers

## Features
- NDVI (Vegetation Health)
- LST (Temperature)
- Drought Prediction (ML Model)
- Farmer Credit Score

## Tech Stack
- FastAPI (Backend)
- Streamlit (Frontend)
- XGBoost (ML)
- Google Earth Engine

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload
```

Set `JWT_SECRET_KEY` in `.env` to a long, random value before deployment. The
application refuses to start in production when the development secret is in
use. `DATABASE_URL` defaults to a local SQLite database (`terrascore.db`) and
may be changed to a production SQLAlchemy-compatible database URL.

## Authentication

The existing ML APIs (`POST /train` and `POST /predict`) are unchanged.

- `POST /signup` registers a user. Supply `email`, an 8+ character `password`,
  and optionally `full_name`.
- `POST /login` accepts `email` and `password`, then returns a bearer JWT.
- `GET /profile` requires `Authorization: Bearer <access_token>` and returns
  the authenticated user's safe profile fields.

Example:

```bash
curl -X POST http://127.0.0.1:8001/signup \
  -H 'Content-Type: application/json' \
  -d '{"email":"farmer@example.com","password":"SafePassword123!"}'

curl -X POST http://127.0.0.1:8001/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"farmer@example.com","password":"SafePassword123!"}'
```

## Backend authentication layout

- `backend/config.py` reads and validates runtime configuration.
- `backend/database/session.py` owns the SQLAlchemy engine and session lifecycle.
- `backend/models/user.py` defines the persistent user table.
- `backend/schemas/auth.py` validates auth requests and prevents password data
  from appearing in responses.
- `backend/services/auth.py` contains bcrypt and JWT operations.
- `backend/routers/auth.py` provides the signup, login, and protected profile routes.
- `backend/main.py` is the production ASGI entrypoint; `backend/api.py` remains
  compatible with the previous application command.

## Database

SQLite is the default database and is configured through `DATABASE_URL`. The
SQLAlchemy domain model includes users, farms, predictions, reports, and
training history. Existing ML endpoints remain unchanged and do not require a
database migration to preserve their current API contract.

In development, the application creates a fresh SQLite schema at startup. In
production, automatic schema creation is disabled; run the migration as part
of deployment before starting the API.

For a managed deployment, apply the versioned schema rather than relying on
startup table creation:

```bash
alembic upgrade head
```

## Production API features

- Prediction history: `GET /predictions`, `GET /prediction/{id}`, and `DELETE /prediction/{id}`.
- Farm management: `POST|GET /farm`, `PUT|DELETE /farm/{id}`.
- Authenticated `/predict` calls are stored automatically and include climate context plus agronomic recommendations.
- Forecasts: `GET /forecast?latitude=28.4&longitude=77.0` returns a seven-day Open-Meteo forecast.
- Reports and analytics: `GET /report/{prediction_id}`, `GET /dashboard`, and `GET /analytics`.
- Bulk scoring: `POST /upload` accepts CSV/XLSX with `latitude`, `longitude`, `start_date`, and `end_date`, then returns a downloadable CSV.
- Administration: `/admin/login`, `/admin/users`, `/admin/farms`, `/admin/predictions`, and `/admin/statistics` require an administrator account.

Swagger documentation is available at `/docs`; request models provide validation
constraints and examples, while route metadata documents behavior and errors.
