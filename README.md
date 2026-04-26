# Beauty Decision Assistant MVP Scaffold

Minimal scaffold for a personalized beauty decision assistant web app.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python -m app.backend.main
```

4. Open:

```text
http://127.0.0.1:8000
```

## Production notes

- The server binds to `0.0.0.0` and reads the port from the `PORT` environment variable.
- Static assets are served from `app/frontend` at `/static`.
- The landing page is served from `/`.
- Health check: `GET /api/health`

## Deploy

### Backend on Render

1. Create a new Render Blueprint or Web Service from this repository.
2. If using the Blueprint, Render will read `render.yaml`.
3. Set `CORS_ALLOW_ORIGINS` to your Vercel frontend URL, such as `https://your-app.vercel.app`.
4. Deploy and copy the Render service URL.

### Frontend on Vercel

1. Import this repository into Vercel.
2. Set the Root Directory to `app/frontend`.
3. Set the production environment variable `API_BASE_URL` to your Render backend URL, such as `https://your-api.onrender.com`.
4. Deploy. Vercel will use `app/frontend/vercel.json` and build the static frontend into `app/frontend/dist`.

## Current scope

- one-page frontend
- FastAPI backend
- review ingestion from `data/reviews.json`
- ad filtering, ranking, explanations, and trust scoring
- deployable single-service app
