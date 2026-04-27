import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.backend.api.routes import router as api_router
from app.backend.database import init_database


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "app" / "frontend"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
FRONTEND_STATIC_DIR = FRONTEND_DIST_DIR / "static"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
app = FastAPI(
    title="Beauty Decision Assistant",
    description="Minimal MVP scaffold for personalized beauty recommendations.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_event_handler("startup", init_database)
app.include_router(api_router, prefix="/api")
app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="static")


@app.get("/")
async def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIST_DIR / "index.html")


def run() -> None:
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(
        "app.backend.main:app",
        host="0.0.0.0",
        port=port,
    )


if __name__ == "__main__":
    run()
