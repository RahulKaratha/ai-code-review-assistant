from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "AI-powered semantic code review service integrated with CI/CD pipelines."
    ),
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

_INDEX_HTML = (Path(__file__).parent / "templates" / "index.html").read_text(
    encoding="utf-8"
)


@app.get("/", include_in_schema=False)
def index():
    return HTMLResponse(_INDEX_HTML)


app.include_router(router)
