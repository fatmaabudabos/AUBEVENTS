"""This file defines the **Pydantic schemas** (data validation and serialization classes) 
used for the Event management feature in the backend.

Schemas serve two main purposes:
1. **Validation**: Ensure that the data coming from the frontend matches the rules 
   (e.g., capacity > 1, organizers/speakers cannot be empty).
2. **Serialization**: Define the exact shape of JSON sent back to the frontend.

How they are used:
- EventCreate → for POST /api/events (creating new events)
- EventUpdate → for PATCH /api/events/{id} (updating existing events)
- EventOut    → for GET /api/events/{id} (fetching event details)

Required pip installs:
- pydantic (for BaseModel and validation)
- fastapi (depends on Pydantic internally, used in routes)
- sqlmodel (for database models, though schemas are separate)

Install with:
    pip install fastapi pydantic sqlmodel
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator


# -------------------------
# Base schema (shared fields)
# -------------------------
class EventBase(BaseModel):
    """
    Base class for event schemas.
    Contains all possible fields, mostly optional.
    Validation rules are defined here so they apply to both
    create and update operations.
    """

    title: Optional[str]
    description: Optional[str] = None
    date: Optional[datetime]
    location: Optional[str]
    capacity: Optional[int]
    organizers: Optional[List[str]]
    speakers: Optional[List[str]]

    # Validation rules
    @validator("capacity")
    def capacity_gt_one(cls, v):
        """
        Capacity must be > 1 if provided.
        """
        if v is not None and v <= 1:
            raise ValueError("Invalid capacity (must be > 1)")
        return v

    @validator("organizers")
    def organizers_non_empty(cls, v):
        """
        Organizers list cannot be empty if provided.
        """
        if v is not None and len(v) == 0:
            raise ValueError("Organizers cannot be empty")
        return v

    @validator("speakers")
    def speakers_non_empty(cls, v):
        """
        Speakers list cannot be empty if provided.
        """
        if v is not None and len(v) == 0:
            raise ValueError("Speakers cannot be empty")
        return v


# -------------------------
# Create schema
# -------------------------
class EventCreate(EventBase):
    """
    Schema for creating a new event.
    All important fields are required here.
    """

    title: str
    date: datetime
    location: str
    capacity: int
    organizers: List[str]
    speakers: List[str]


# -------------------------
# Update schema
# -------------------------
class EventUpdate(BaseModel):
    """
    Schema for updating an event.
    All fields are optional, because PATCH may include only the changed fields.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[datetime] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    organizers: Optional[List[str]] = None
    speakers: Optional[List[str]] = None


# -------------------------
# Output schema
# -------------------------
class EventOut(BaseModel):
    """
    Schema for returning an event to the frontend.
    Matches exactly what the frontend expects when it fetches an event.
    """

    id: int
    title: str
    description: Optional[str]
    date: datetime
    location: str
    capacity: int
    available_seats: Optional[int]
    organizers: List[str]
    speakers: List[str]

    class Config:
        from_attributes = True  # allows reading from SQLModel/ORM objects


class UserEventAction(BaseModel):
    """Schema for user actions on an event (register/unregister)."""
    event_id: int
    email: str

class UserEventResponse(BaseModel):
    """Standardized response for user-event operations."""
    success: bool
    message: str