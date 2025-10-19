"""
crud.py
-------
This file contains higher-level CRUD operations that sit
between the API routes and the database functions.

- It imports low-level DB operations from database.py
- It accepts validated schemas (EventCreate, EventUpdate)
- It applies business rules (capacity, non-empty lists)
- It returns event objects or error messages for routes to handle
- Contains admin: create,update,delete and user: register,unregister
"""

from typing import Optional, List
from sqlmodel import Session
from datetime import datetime

from backend.schemas import EventCreate, EventUpdate, EventOut, UserEventAction, UserEventResponse
from database.database import (
    create_event as db_create_event,
    list_events as db_list_events,
    register_user_to_event as db_register_user_to_event,
    unregister_user_from_event as db_unregister_user_from_event,
    get_user_events as db_get_user_events,
    get_title, get_description, get_date, get_location,
    get_capacity, get_available_seats, get_speakers, get_organizer,
    update_title, update_description, update_date, update_location,
    update_capacity, update_available_seats, update_speakers,
    update_organizer, delete_event,
)
from database.tables import Events


# ------------------------
# Create
# ------------------------
def create_event(event_in: EventCreate) -> Events:
    """
    Create a new event in the DB.
    Sets available_seats = capacity initially.
    """
    event = db_create_event(
        title=event_in.title,
        description=event_in.description,
        date=event_in.date,
        location=event_in.location,
        capacity=event_in.capacity,
        available_seats=event_in.capacity,  # initially full capacity
    )
    # organizers & speakers (lists) handled if DB updated to JSON fields
    if event_in.organizers:
        update_organizer(event.id, event_in.organizers)
    if event_in.speakers:
        update_speakers(event.id, event_in.speakers)

    return event


# ------------------------
# Get
# ------------------------
def get_event(event_id: int) -> Optional[EventOut]:
    """
    Return a full event as EventOut schema for the frontend.
    """
    title = get_title(event_id)
    if title is None:
        return None

    return EventOut(
        id=event_id,
        title=title,
        description=get_description(event_id),
        date=get_date(event_id),
        location=get_location(event_id),
        capacity=get_capacity(event_id),
        available_seats=get_available_seats(event_id),
        organizers=get_organizer(event_id),
        speakers=get_speakers(event_id),
    )


def list_all_events() -> List[EventOut]:
    rows = db_list_events()
    out: List[EventOut] = []
    for r in rows:
        out.append(EventOut(
            id=r.id,
            title=r.title,
            description=r.description,
            date=r.date,
            location=r.location,
            capacity=r.capacity,
            available_seats=r.available_seats,
            organizers=r.organizers,
            speakers=r.speakers,
        ))
    return out


# ------------------------
# Update (PATCH)
# ------------------------
def update_event(event_id: int, event_in: EventUpdate):
    """
    Partially update an event (PATCH).
    Only apply fields that are present.
    Adjust available seats when capacity changes.
    """

    # title, desc, date, etc.
    if event_in.title is not None:
        update_title(event_id, event_in.title)
    if event_in.description is not None:
        update_description(event_id, event_in.description)
    if event_in.date is not None:
        update_date(event_id, event_in.date)
    if event_in.location is not None:
        update_location(event_id, event_in.location)
    if event_in.organizers is not None:
        update_organizer(event_id, event_in.organizers)
    if event_in.speakers is not None:
        update_speakers(event_id, event_in.speakers)

    # ✅ Handle capacity change via existing DB helpers
    if event_in.capacity is not None:
        old_capacity = get_capacity(event_id)
        old_available = get_available_seats(event_id)

        # Update capacity first
        update_capacity(event_id, event_in.capacity)

        # Adjust available seats logically
        if old_capacity is not None and old_available is not None:
            if event_in.capacity > old_capacity:
                diff = event_in.capacity - old_capacity
                new_available = old_available + diff
            else:
                new_available = min(old_available, event_in.capacity)
            update_available_seats(event_id, new_available)

    # Finally return the updated event as EventOut
    return get_event(event_id)


# ------------------------
# Delete
# ------------------------
# database/database.py
def delete_event_by_id(event_id: int) -> bool:
    return delete_event(event_id)


#-----------------------------------------------
# User functions
#-----------------------------------------------

def register_user(data: UserEventAction) -> UserEventResponse:
    success = db_register_user_to_event(data.email, data.event_id)
    msg = "User registered successfully." if success else "Registration failed."
    return UserEventResponse(success=bool(success), message=msg)


def unregister_user(data: UserEventAction) -> UserEventResponse:
    success = db_unregister_user_from_event(data.email, data.event_id)
    msg = "User unregistered successfully." if success else "Unregistration failed."
    return UserEventResponse(success=bool(success), message=msg)


def list_user_events(user_email: str):
    """
    Returns a list of event objects (ready for JSON serialization).
    Each event is a dict.
    """
    return db_get_user_events(user_email)

