# api/events.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from database.database import engine
from database.tables import Events, Users
# Note: You need to implement this dependency or adjust import to your auth
# For example, it should decode JWT and return a Users instance
from auth.auth_utils import get_current_user  # or your existing auth dependency

router = APIRouter(prefix="/api/events", tags=["Events"])


def get_session():
    with Session(engine) as session:
        yield session


# Pydantic model for incoming event data
from pydantic import BaseModel

class EventCreate(BaseModel):
    title: str
    description: str
    date: datetime
    location: str
    capacity: int
    available_seats: int
    speakers: List[str]
    organizers: List[str]


# Admin-only endpoint to create an event
@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreate,
    s: Session = Depends(get_session),
    current_user: Users = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create events")

    event = Events(
        title=payload.title,
        description=payload.description,
        date=payload.date,
        location=payload.location,
        capacity=payload.capacity,
        available_seats=payload.available_seats,
        speakers=payload.speakers,
        organizers=payload.organizers
    )

    s.add(event)
    s.commit()
    s.refresh(event)
    return {"message": "Event created", "id": event.id}
