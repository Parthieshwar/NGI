# main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
from chatbot.chatbot import chain, memory, retriever
from typing import AsyncGenerator
import logging
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    memory.clear()
    logging.info("Memory cleared on app startup.")
    
    yield
    
    memory.clear()
    logging.info("Memory cleared on app shutdown.")


app = FastAPI(title="NGI Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    question: str

async def stream_response(query: str) -> AsyncGenerator[str, None]:
    memory.add_human_message(query)
    response_text = ""

    try:
        async for chunk in chain.astream({
            "question": query,
            "context": "\n".join([doc.page_content for doc in retriever.get_relevant_documents(query)]),
            "memory": memory.get_memory_text()
        }):
            text = chunk.content if hasattr(chunk, "content") else str(chunk)
            response_text += text
            yield f"data: {text}\n\n"  # SSE chunk
            await asyncio.sleep(0.01)
    except Exception as e:
        yield f"data: Error: {str(e)}\n\n"

    memory.add_ai_message(response_text)
    # **Send [DONE] to signal frontend the stream is complete**
    yield "data: [DONE]\n\n"


@app.get("/stream")
async def stream_chat(question: str, reset: bool = False):
    if reset:
        memory.clear()  # Make sure your memory object has a clear() method
        
    return StreamingResponse(stream_response(question), media_type="text/event-stream")