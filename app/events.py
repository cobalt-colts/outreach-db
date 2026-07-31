from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_events, get_session

events = APIRouter(prefix="/events", tags=["events"])

@events.get("/get")
async def _api_events_get(session: Session = Depends(get_session)):
    return get_events(session=session)