# Deploying TerraScore

## Docker

1. Copy `.env.example` to `.env` and set a strong `JWT_SECRET_KEY`.
2. Start the API with `docker compose up --build`.
3. Open `http://localhost:8000/docs`.

The Compose setup keeps SQLite and logs in named volumes. For any multi-instance
deployment, replace SQLite with PostgreSQL by setting `DATABASE_URL` and run
`alembic upgrade head` before starting the service.

## Render

Push this repository and create a Blueprint from `render.yaml`. Set
`DATABASE_URL` to Render PostgreSQL's internal connection URL and provide the
other values from `.env.example`. In the deploy command or release step run
`alembic upgrade head` before the web process starts.

## Railway

Create a project from the repository, add a PostgreSQL service, then set
`DATABASE_URL`, `ENVIRONMENT=production`, and `JWT_SECRET_KEY`. Railway detects
the Dockerfile. Run `alembic upgrade head` in a one-off command after each
schema deployment.

## AWS EC2

Install Docker and the Compose plugin, clone the repository, configure `.env`,
then run `docker compose up -d --build`. Place the instance behind an HTTPS
load balancer or reverse proxy. Use PostgreSQL/RDS rather than local SQLite for
durable multi-instance production deployments.
