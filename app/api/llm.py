from typing import Optional
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm import stream_prompt

router = APIRouter(prefix="/api", tags=["AI"])

class PromptRequest(BaseModel):
    prompt: str
    data_context: Optional[str] = None
    previous_prompt: Optional[str] = None
    previous_response: Optional[str] = None

@router.post("/prompt/stream")
async def prompt_stream(request: PromptRequest):
    return StreamingResponse(
        stream_prompt(
            prompt_text=request.prompt,
            data_context=request.data_context,
            previous_prompt=request.previous_prompt,
            previous_response=request.previous_response
        ),
        media_type="text/plain; charset=utf-8"
    )