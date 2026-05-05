from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()

# Get the path to the pages directory
BASE_DIR = Path(__file__).resolve().parent.parent
PAGES_DIR = BASE_DIR / "pages"


# HOME PAGE
@router.get("/home", response_class=FileResponse, summary="Home page")
async def get_home():
    home_html = PAGES_DIR / "home.html"
    return FileResponse(home_html)

# Graph input (making the graph area)
@router.get("/graph-input", response_class=FileResponse, summary="Graph input page")
async def get_graph_input():
    graph_input_html = PAGES_DIR / "graph-input.html"
    return FileResponse(graph_input_html)

# graph output (displaying the graph page)
@router.get("/graph-output", response_class=FileResponse, summary="Graph output page")
async def get_graph_output():
    graph_output_html = PAGES_DIR / "graph-output.html"
    return FileResponse(graph_output_html)

@router.get("/help", response_class=FileResponse, summary="Help page")
async def get_help():
    help_html = PAGES_DIR / "help.html"
    return FileResponse(help_html)
