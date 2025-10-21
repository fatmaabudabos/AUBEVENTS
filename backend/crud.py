"""
crud.py
-------
Higher-level CRUD operations that sit between API routes and DB functions.

- Imports low-level DB operations from database.py
- Accepts validated schemas (EventCreate, EventUpdate)
- Applies business rules (capacity, non-empty lists)
- Returns EventOut objects or simple status responses for routes to handle
- Contains admin: create, update, delete and user: register, unregister
"""

from typing import Optional, List, Any
from datetime import datetime

from backend.schemas import (
    EventCreate,
    EventUpdate,
    EventOut,
    UserEventAction,
    UserEventResponse,
)
from database.database import (
    create_event as db_create_event,
    list_events as db_list_events,
    register_user_to_event as db_register_user_to_event,
    unregister_user_from_event as db_unregister_user_from_event,
    get_user_events as db_get_user_events,
    get_title,
    get_description,
    get_date,
    get_location,
    get_capacity,
    get_available_seats,
    get_speakers,
    get_organizer,
    update_title,
    update_description,
    update_date,
    update_location,
    update_capacity,
    update_available_seats,
    update_speakers,
    update_organizer,
    delete_event,
)
from database.tables import Events


# ------------------------
# Helpers
# ------------------------
def _row_to_eventout(r: Any) -> EventOut:
    """
    Convert a DB row/object (with dot attributes) into EventOut.
    Safely handles optional attributes (organizers/speakers may be None).
    """
    return EventOut(
        id=r.id,
        title=getattr(r, "title", None),
        description=getattr(r, "description", None),
        date=getattr(r, "date", None),
        location=getattr(r, "location", None),
        capacity=getattr(r, "capacity", None),
        available_seats=getattr(r, "available_seats", None),
        organizers=getattr(r, "organizers", []) or [],
        speakers=getattr(r, "speakers", []) or [],
    )


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
    # organizers & speakers (lists) handled if DB supports JSON/text arrays
    if event_in.organizers:
        update_organizer(event.id, event_in.organizers)
    if event_in.speakers:
        update_speakers(event.id, event_in.speakers)

    return event


# ------------------------
# Get (single + list)
# ------------------------
def get_event(event_id: int) -> Optional[EventOut]:
    """
    Return a full event as EventOut for the frontend; None if not found.
    (Pulls scalar fields using your DB accessors.)
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
        organizers=get_organizer(event_id) or [],
        speakers=get_speakers(event_id) or [],
    )


def list_all_events() -> List[EventOut]:
    """
    Return all events as EventOut, ordered by whatever db_list_events provides.
    """
    rows = db_list_events()
    return [_row_to_eventout(r) for r in rows]


# ------------------------
# Update (PATCH)
# ------------------------
def update_event(event_id: int, event_in: EventUpdate) -> Optional[EventOut]:
    """
    Partially update an event (PATCH). Only apply provided fields.
    Adjust available seats logically when capacity changes.
    Returns the updated EventOut, or None if the event no longer exists.
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

    # Handle capacity/available_seats coupling
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

    return get_event(event_id)


# ------------------------
# Delete
# ------------------------
def delete_event_by_id(event_id: int) -> bool:
    """
    Delete event and return True if successful.
    """
    return delete_event(event_id)


# -----------------------------------------------
# User functions
# -----------------------------------------------
def register_user(data: UserEventAction) -> UserEventResponse:
    """
    Register a user (by email) to an event (by id).
    """
    success = db_register_user_to_event(data.email, data.event_id)
    msg = "User registered successfully." if success else "Registration failed."
    return UserEventResponse(success=bool(success), message=msg)


def unregister_user(data: UserEventAction) -> UserEventResponse:
    """
    Unregister a user (by email) from an event (by id).
    """
    success = db_unregister_user_from_event(data.email, data.event_id)
    msg = "User unregistered successfully." if success else "Unregistration failed."
    return UserEventResponse(success=bool(success), message=msg)


def list_user_events(user_email: str) -> List[EventOut]:
    """
    Return all events that a given user is registered for, as EventOut list.
    """
    rows = db_get_user_events(user_email)
    return [_row_to_eventout(r) for r in rows]
