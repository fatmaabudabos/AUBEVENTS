"""
crud.py
-------
This file contains higher-level CRUD operations that sit
between the API routes and the database functions.

- It imports low-level DB operations from database.py
- It accepts validated schemas (EventCreate, EventUpdate)
- It applies business rules (capacity, non-empty lists)
- It returns event objects or error messages for routes to handle
"""

from typing import Optional
from sqlmodel import Session
from datetime import datetime

from backend.schemas import EventCreate, EventUpdate, EventOut
from database.database import (
    create_event as db_create_event,
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
        organizers=get_organizer(event_id),
        speakers=get_speakers(event_id),
    )


# ------------------------
# Update (PATCH)
# ------------------------
def update_event(event_id: int, event_in: EventUpdate) -> Optional[Events]:
    """
    Partially update an event (PATCH).
    Only apply fields that are present.
    """

    if event_in.title is not None:
        update_title(event_id, event_in.title)
    if event_in.description is not None:
        update_description(event_id, event_in.description)
    if event_in.date is not None:
        update_date(event_id, event_in.date)
    if event_in.location is not None:
        update_location(event_id, event_in.location)
    if event_in.capacity is not None:
        update_capacity(event_id, event_in.capacity)
    if event_in.organizers is not None:
        update_organizer(event_id, event_in.organizers)
    if event_in.speakers is not None:
        update_speakers(event_id, event_in.speakers)

    # After updates, return the updated object as DB model
    # (you could also return EventOut here if cleaner for routes)
    return get_event(event_id)


# ------------------------
# Delete
# ------------------------
def delete_event_by_id(event_id: int) -> bool:
    """
    Delete an event by ID.
    Returns True if deleted, False if not found.
    """
    return delete_event(event_id) is not None
