import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.app.api.routes import battle

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Rap Battle")

# Set up the paths for static files
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/", response_class=FileResponse)
async def read_root():
    return STATIC_DIR / "index.html"


@app.get("/battle-ui", response_class=FileResponse)
async def battle_page():
    return STATIC_DIR / "battle-ui.html"


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


app.include_router(battle.router, prefix="/battle", tags=["battle"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)