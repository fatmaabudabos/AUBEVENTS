"""
Comprehensive integration test for backend.crud module.
Covers admin (create, get, update, delete) and user (register/unregister/list) functions.
"""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel

from database.database import get_engine
from database.tables import Users
from backend.crud import (
    create_event,
    get_event,
    list_all_events,
    update_event,
    delete_event_by_id,
    register_user,
    unregister_user,
    list_user_events,
)
from backend.schemas import EventCreate, EventUpdate, UserEventAction


# --------------------------------------------------------------------
# Fixtures: setup and teardown
# --------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_db():
    """Recreate a clean database before each test."""
    engine = get_engine()
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def sample_user():
    """Insert a verified user for registration tests."""
    with Session(get_engine()) as session:
        user = Users(email="student@aub.edu.lb", password_hash="hashed_pw", is_verified=True)
        session.add(user)
        session.commit()
        return user.email


@pytest.fixture
def sample_event_data():
    """Return a base event creation schema."""
    return EventCreate(
        title="Hackathon 2025",
        description="Annual AUB Hackathon event.",
        date=datetime.utcnow() + timedelta(days=7),
        location="AUB Campus",
        capacity=3,
        available_seats=3,
        organizers=["CS Society"],
        speakers=["Dr. Lina"],
    )


# --------------------------------------------------------------------
# Admin CRUD Tests
# --------------------------------------------------------------------

def test_create_and_get_event(sample_event_data):
    event = create_event(sample_event_data)
    assert event.id is not None
    fetched = get_event(event.id)
    assert fetched.title == "Hackathon 2025"
    assert fetched.capacity == 3
    assert fetched.available_seats == 3


def test_list_all_events(sample_event_data):
    create_event(sample_event_data)
    create_event(EventCreate(
        title="Tech Talk",
        description="AI at AUB",
        date=datetime.utcnow(),
        location="AUB Campus",
        capacity=2,
        available_seats=2,
        organizers=["AI Club"],
        speakers=["Dr. Karim"]
    ))

    events = list_all_events()
    assert len(events) == 2
    titles = [e.title for e in events]
    assert "Hackathon 2025" in titles and "Tech Talk" in titles


def test_update_event(sample_event_data):
    event = create_event(sample_event_data)
    patch = EventUpdate(
        title="Hackathon 2025 – Updated",
        capacity=5,
        location="Beirut Digital District"
    )
    updated = update_event(event.id, patch)
    assert updated.title == "Hackathon 2025 – Updated"
    assert updated.capacity == 5
    assert updated.location == "Beirut Digital District"
    assert updated.available_seats == 5


def test_delete_event(sample_event_data):
    event = create_event(sample_event_data)
    result = delete_event_by_id(event.id)
    assert result is True
    result2 = delete_event_by_id(event.id)
    assert result2 is False


# --------------------------------------------------------------------
# User CRUD Tests (using schemas)
# --------------------------------------------------------------------

def test_register_user_to_event(sample_user, sample_event_data):
    event = create_event(sample_event_data)
    data = UserEventAction(event_id=event.id, email=sample_user)

    resp = register_user(data)
    assert resp.success is True
    assert "success" in resp.message.lower()

    events = list_user_events(sample_user)
    assert len(events) == 1
    assert events[0]["title"] == "Hackathon 2025"


def test_register_user_event_full(sample_user, sample_event_data):
    """Should fail when event is full."""
    sample_event_data.capacity = 1
    event = create_event(sample_event_data)

    # Register first user
    first = register_user(UserEventAction(event_id=event.id, email=sample_user))
    assert first.success is True

    # Create another user
    with Session(get_engine()) as session:
        u2 = Users(email="other@aub.edu.lb", password_hash="pw", is_verified=True)
        session.add(u2)
        session.commit()

    # Try registering second user -> should fail
    second = register_user(UserEventAction(event_id=event.id, email="other@aub.edu.lb"))
    assert second.success is False
    assert "full" in second.message.lower() or "fail" in second.message.lower()


def test_unregister_user_from_event(sample_user, sample_event_data):
    event = create_event(sample_event_data)
    register_user(UserEventAction(event_id=event.id, email=sample_user))

    resp = unregister_user(UserEventAction(event_id=event.id, email=sample_user))
    assert resp.success is True
    assert "unregistered" in resp.message.lower()

    events = list_user_events(sample_user)
    assert len(events) == 0

    # Unregister again -> should fail
    resp2 = unregister_user(UserEventAction(event_id=event.id, email=sample_user))
    assert resp2.success is False
