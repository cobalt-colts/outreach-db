from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import Session, SQLModel

from app.auth import get_auth_payload
from app.database import get_events, get_session, create_event
from app.models import OutreachEventAPI

events = APIRouter(prefix="/events", tags=["events"])

@events.get("/get")
async def _api_events_get(session: Session = Depends(get_session)):
    return get_events(session=session)

@events.post("/create")
async def _api_events_create(
        body: OutreachEventAPI,
        session: Session = Depends(get_session),
        payload: dict[str, Any] = Depends(get_auth_payload)
):
    perms = payload.get('permissions')
    if perms != 0:
        raise HTTPException(status_code=403, detail="Unauthorized to create events.")

    if not body.link.startswith("https://") or body.link.startswith("http://"):
        body.link = "https://" + body.link

    try:
        create_event(session, body)
    except SQLAlchemyError as e:
        raise HTTPException(status_code=501, detail="Unable to create event.")