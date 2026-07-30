# Database migrations

This directory is managed by Alembic. The migrations create the `users`,
`farms`, `predictions`, `reports`, and `training_history` tables, then add
prediction climate/recommendation fields and administrator authorization.

Use migrations in deployed environments rather than `Base.metadata.create_all`:

```bash
alembic upgrade head
```

After a model change, review the generated migration before applying it:

```bash
alembic revision --autogenerate -m "describe schema change"
alembic upgrade head
```
