# Beauty Decision Assistant MVP Scaffold

Minimal scaffold for a personalized beauty decision assistant web app.

## Run locally

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Build the React frontend:

```bash
cd app/frontend
npm install
npm run build
```

4. Start the app:

```bash
python -m app.backend.main
```

5. Open:

```text
http://127.0.0.1:8000
```

## Frontend development

Run the React frontend locally with Vite:

```bash
cd app/frontend
npm install
npm run dev
```

Set `API_BASE_URL=http://127.0.0.1:8000` if you want the Vite dev server to call the local FastAPI backend. If you do not set it, the frontend uses relative `/api` paths.

## Production notes

- The server binds to `0.0.0.0` and reads the port from the `PORT` environment variable.
- Static assets are served from `app/frontend/dist/static` at `/static`.
- The landing page is served from `/`.
- Health check: `GET /api/health`

## Deploy

### Backend on Render

1. Create a new Render Blueprint or Web Service from this repository.
2. If using the Blueprint, Render will read `render.yaml`.
3. Set `CORS_ALLOW_ORIGINS` to your Vercel frontend URL, such as `https://your-app.vercel.app`.
   The backend also allows `https://*.vercel.app` by default through `CORS_ALLOW_ORIGIN_REGEX`.
4. Deploy and copy the Render service URL.

### Frontend on Vercel

1. Import this repository into Vercel.
2. Set the Root Directory to `app/frontend`.
   If Vercel is trying to detect FastAPI or shows `No fastapi entrypoint found`, it is building the wrong directory.
   In that case, change the Root Directory to `app/frontend` and set the Framework Preset to `Vite` or `Other`.
3. You can leave `API_BASE_URL` empty on Vercel. The Vercel config rewrites `/api/*` to `https://beauty-agent-cufm.onrender.com/api/*`, which avoids browser CORS issues.
4. Deploy. Vercel will use `app/frontend/vercel.json` and build the React app into `app/frontend/dist`.

## Current scope

- React + Tailwind frontend
- FastAPI backend
- review ingestion from `data/reviews.json`
- ad filtering, ranking, explanations, and trust scoring
- deployable single-service app
