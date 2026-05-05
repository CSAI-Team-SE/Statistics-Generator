from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from app.services.graph import process_graph_request

router = APIRouter()

# Post route to collect graph input
@router.post("/graph-generate")
async def generate_graph(request: Request):
    data = await request.json()
    return JSONResponse(process_graph_request(data))
