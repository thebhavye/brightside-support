"""The Brightside Bikes website: a support page with a chat box backed by bot.answer."""

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

import bot
import medic_runtime as medic
import neatlogs
import os

# Traced into neatlogs with the release and environment Medic needs (added by agent-medic init).
if not os.environ.get("MEDIC_RUNNER"):          # Medic's own runs initialize neatlogs themselves
    neatlogs.init(workflow_name="brightside-support",
                  tags=["env:" + os.environ.get("MEDIC_ENV", "prod"),
                        "release:" + os.environ.get("GIT_SHA", "dev")[:12]],
                  instrumentations=["openai"])

app = FastAPI(title="Brightside Bikes support")


class ChatRequest(BaseModel):
    message: str


class ChatReply(BaseModel):
    reply: str


@app.post("/api/chat")
@medic.entrypoint
def chat(req: ChatRequest) -> ChatReply:
    return ChatReply(reply=bot.answer(req.message))


@app.get("/")
def home():
    return FileResponse("static/index.html")


# Added by agent-medic init: Medic asks your agent its known-answer questions through this.
def medic_answer(question: str):
    return chat(ChatRequest(message=question))
