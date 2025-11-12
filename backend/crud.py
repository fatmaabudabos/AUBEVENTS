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
    get_image_url,
    get_capacity,
    get_available_seats,
    get_speakers,
    get_category,
    get_organizer,
    update_title,
    update_description,
    update_date,
    update_location,
    update_image_url,
    update_capacity,
    update_available_seats,
    update_speakers,
    update_organizer,
    update_category,
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
    Note: created_by is not included in EventOut as it's for internal use only.
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
        category=getattr(r, "category", None),
        image_url=getattr(r, "image_url", None),
    )


# ------------------------
# Create
# ------------------------
def create_event(event_in: EventCreate, created_by: Optional[str] = None) -> Events:
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
        category=event_in.category if hasattr(event_in, 'category') else None,
        created_by=created_by,
        image_url=getattr(event_in, "image_url", None),
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
        category=get_category(event_id),
        image_url=get_image_url(event_id),
    )


def list_all_events(search: Optional[str] = None) -> List[EventOut]:
    """
    Return events as EventOut; if `search` provided, filter by title/location/description.
    """
    rows = db_list_events(search)
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
    if getattr(event_in, "image_url", None) is not None:
        update_image_url(event_id, event_in.image_url)
    if event_in.organizers is not None:
        update_organizer(event_id, event_in.organizers)
    if event_in.speakers is not None:
        update_speakers(event_id, event_in.speakers)
    if getattr(event_in, "category", None) is not None:
        update_category(event_id, event_in.category)

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
    success, reason = db_register_user_to_event(data.email, data.event_id)
    if success:
        msg = "User registered successfully."
    else:
        if reason == 'full':
            msg = "Event is full."
        elif reason == 'already_registered':
            msg = "User already registered for event."
        elif reason == 'not_found':
            msg = "User or event not found."
        else:
            msg = "Registration failed."
    return UserEventResponse(success=bool(success), message=msg, reason=reason)


def unregister_user(data: UserEventAction) -> UserEventResponse:
    """
    Unregister a user (by email) from an event (by id).
    """
    success = db_unregister_user_from_event(data.email, data.event_id)
    msg = "User unregistered successfully." if success else "Unregistration failed."
    return UserEventResponse(success=bool(success), message=msg)


def list_user_events(user_email: str, search: Optional[str] = None) -> List[EventOut]:
    """
    Return events that a given user is registered for, as EventOut list.
    If `search` provided, filter by title/location/description.
    """
    rows = db_get_user_events(user_email, search)
    out: list[EventOut] = []
    from datetime import datetime
    for r in rows:
        # db_get_user_events may return DB model objects (with attributes) or dicts
        if isinstance(r, dict):
            # Ensure required EventOut fields are present and valid.
            cap = r.get('capacity')
            if cap is None:
                cap = 2  # sensible default to satisfy EventOut validation (>1)
            dt = r.get('date') or datetime.utcnow()
            out.append(EventOut(
                id=int(r.get('id')),
                title=str(r.get('title') or ''),
                description=r.get('description'),
                date=dt,
                location=str(r.get('location') or ''),
                capacity=int(cap),
                available_seats=r.get('available_seats'),
                organizers=r.get('organizers') or [],
                speakers=r.get('speakers') or [],
                category=r.get('category'),
            ))
        else:
            out.append(_row_to_eventout(r))
    return out
