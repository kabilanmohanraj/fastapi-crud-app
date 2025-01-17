# shared queue for event streaming
import asyncio
from typing import Annotated

from fastapi import Depends

sse_event_queue = asyncio.Queue()

# dependency to share the event queue
def get_queue() -> asyncio.Queue:
    return sse_event_queue

SSEQueueDep = Annotated[asyncio.Queue, Depends(get_queue)]