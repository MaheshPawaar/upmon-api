from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.api.monitors import router as monitors_router
from app.api.checks import router as checks_router
from app.api.stats import router as stats_router

app = FastAPI(title="Uptime Monitor API")

app.include_router(auth_router)
app.include_router(monitors_router)
app.include_router(checks_router)
app.include_router(stats_router)


@app.get("/")
def health():
    return {"status": "ok"}
