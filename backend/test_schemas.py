# backend/test_schemas.py
from schemas import EventCreate, EventUpdate
from datetime import datetime

def test_valid_schema():
    event = EventCreate(
        title="AI Summit",
        date=datetime(2025, 10, 22, 14, 0),
        location="Main Hall",
        capacity=100,
        organizers=["AUB CS"],
        speakers=["Dr. X", "Dr. Y"],
    )
    print("✅ Valid schema passed:", event.model_dump())

def test_invalid_capacity():
    try:
        EventCreate(
            title="Bad Event",
            date=datetime(2025, 10, 22, 14, 0),
            location="Main Hall",
            capacity=0,
            organizers=["AUB CS"],
            speakers=["Dr. X"],
        )
    except Exception as e:
        print("✅ Invalid capacity caught:", e)

def test_empty_speakers():
    try:
        EventCreate(
            title="No Speakers",
            date=datetime(2025, 10, 22, 14, 0),
            location="Main Hall",
            capacity=10,
            organizers=["AUB CS"],
            speakers=[],
        )
    except Exception as e:
        print("✅ Empty speakers caught:", e)

if __name__ == "__main__":
    test_valid_schema()
    test_invalid_capacity()
    test_empty_speakers()
