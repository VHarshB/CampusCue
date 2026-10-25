"""The small web API that CampusCue (on Cubbie) calls to share an event into a linked Discord channel."""

from __future__ import annotations

from typing import Protocol

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .events import from_dict
from .models import Event


class Sharer(Protocol):
    async def share_from_cubbie(self, code: str, event: Event, shared_by: str | None) -> int | None: ...


class ShareRequest(BaseModel):
    code: str = Field(min_length=6, max_length=20, description="The code from /rally link")
    title: str | None = Field(default=None, max_length=200)
    url: str | None = Field(default=None, max_length=500)
    starts_at: str | None = Field(default=None, description="ISO 8601, e.g. 2026-10-30T19:00:00-07:00")
    ends_at: str | None = None
    location: str | None = Field(default=None, max_length=200)
    note: str | None = Field(default=None, max_length=300)
    shared_by: str | None = Field(default=None, max_length=40, description="First name to show in the group")


def create_app(sharer: Sharer) -> FastAPI:
    app = FastAPI(title="Rally", docs_url=None, redoc_url=None)

    @app.get("/health")
    async def health():
        return {"ok": True}

    @app.post("/share")
    async def share(req: ShareRequest):
        if not req.title and not req.url:
            raise HTTPException(400, "Send at least a title or a url.")
        event = from_dict(req.model_dump())
        channel_id = await sharer.share_from_cubbie(req.code, event, req.shared_by)
        if channel_id is None:
            raise HTTPException(404, "That Rally code isn't linked to a channel (or Rally is paused there).")
        return {"ok": True, "message": "Shared to your group chat."}

    return app
