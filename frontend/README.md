# TerraScore Web

This is the React 19/Vite frontend. It lives alongside the legacy Streamlit
file (`frontend/app.py`) so existing usage is not removed.

## Run locally

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `VITE_API_BASE_URL` in `.env` to the FastAPI server, normally
`http://127.0.0.1:8005`. Ensure the backend `.env` includes
`http://localhost:5173` in `CORS_ORIGINS`.

## Folders

- `src/components/` contains reusable UI, metrics, and map components.
- `src/layouts/` owns the responsive sidebar and top navigation shell.
- `src/pages/` contains route-level auth, dashboard, prediction, farm, report,
  training, analytics, profile, and settings screens.
- `src/services/` contains Axios and every FastAPI endpoint adapter.
- `src/context/` owns authentication and toast notification state.
- `src/types/` mirrors FastAPI response schemas in TypeScript.
- `src/routes/` configures protected, lazy-loaded routes.
- `src/config/` centralizes browser-visible environment configuration.

## API integration boundaries

The app sends only fields accepted by the current backend. UI areas that need
missing backend endpoints—password reset, profile editing, farm GIS boundary
storage, soil/images, and detailed training metrics—are explicitly marked as
unavailable rather than fabricated with mock data.
