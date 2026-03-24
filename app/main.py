from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.api import home

app = FastAPI(
    title="Seismic Analysis",
    description="AI Powered Seismic Activity Dataset Analysis",
    version="0.1.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Redirect root to /home
@app.get("/")
async def root_redirect():
    return RedirectResponse(url="/home")

app.include_router(home.router)
