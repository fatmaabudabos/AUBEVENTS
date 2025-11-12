# List of tables for the database

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, JSON

class UserEventLink(SQLModel, table=True):
    event_id: int = Field(foreign_key="events.id", primary_key=True)
    user_email: str = Field(foreign_key="users.email", primary_key=True)

class Users(SQLModel, table=True):
    email: str = Field(primary_key=True)
    password_hash: str

    is_admin: bool = Field(default=False)

    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)
    verification_token_expiry: Optional[datetime] = Field(default=None)

    reset_code: Optional[str] = Field(default=None)
    reset_code_expiry: Optional[datetime] = Field(default=None)

    events: List["Events"] = Relationship(back_populates="users", link_model=UserEventLink)

class Events(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    description: Optional[str] = Field(default=None)

    date: Optional[datetime] = Field(default=None)
    location: Optional[str] = Field(default=None)

    capacity: Optional[int] = Field(default=None)
    available_seats: Optional[int] = Field(default=None)

    speakers: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    organizers: List[str] = Field(default_factory=list, sa_column=Column(JSON))

    category: Optional[str] = Field(default=None)
    created_by: Optional[str] = Field(foreign_key="users.email", default=None)
    image_url: Optional[str] = Field(default=None)

    users: List[Users] = Relationship(back_populates="events", link_model=UserEventLink)
