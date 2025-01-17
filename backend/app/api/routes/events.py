import asyncio
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from .shared_queue import SSEQueueDep

router = APIRouter(prefix="/events", tags=["events"])

async def crud_event_stream(q: asyncio.Queue) -> AsyncGenerator[str, None]:
    while True:
        event = await q.get()
        yield f"payload: {event}\n\n"

@router.get(
    "/crud",
    summary="Stream CRUD events",
    description=(
        "Stream real-time CRUD operation events using Server-Sent Events (SSE). "
        "This endpoint returns a continuous stream of events from a shared queue."
    ),
    responses={
        200: {
            "description": "A continuous stream of CRUD events.",
            "content": {"text/event-stream": {}},
        },
    },
)
async def crud_sse_endpoint(q: SSEQueueDep):
    return StreamingResponse(crud_event_stream(q), media_type="text/event-stream")
    