from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

# Get the path to the pages directory
BASE_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE_DIR / "pages"

@router.get("/home", response_class=FileResponse, summary="Home page")
async def get_home():
    home_html = PAGES_DIR / "home.html"
    return FileResponse(home_html)
