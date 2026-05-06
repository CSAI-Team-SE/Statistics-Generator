from typing import Optional, List
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.services.llm import stream_prompt

router = APIRouter(prefix="/api", tags=["AI"])

class ChatMessage(BaseModel):
    role: str
    content: str

class PromptRequest(BaseModel):
    prompt: str
    data_context: Optional[str] = None
    history: Optional[List[ChatMessage]] = None

@router.post("/prompt/stream")
async def prompt_stream(request: PromptRequest):
    return StreamingResponse(
        stream_prompt(
            prompt_text=request.prompt,
            data_context=request.data_context,
            history=request.history
        ),
        media_type="text/plain; charset=utf-8"
    )