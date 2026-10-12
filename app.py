"""The Brightside Bikes website: a support page with a chat box backed by bot.answer."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import bot

app = FastAPI(title="Brightside Bikes support")


class ChatRequest(BaseModel):
    message: str


class ChatReply(BaseModel):
    reply: str


@app.post("/api/chat")
def chat(req: ChatRequest) -> ChatReply:
    return ChatReply(reply=bot.answer(req.message))


@app.get("/")
def home():
    return FileResponse("static/index.html")
