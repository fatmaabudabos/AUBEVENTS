# List of database functions to be used in the backend

from sqlmodel import Session, select, create_engine, SQLModel
from sqlalchemy import or_, update
from database.tables import Users
from database.tables import Events
from database.tables import PendingSignup
from typing import Optional, List
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, echo=False)

def get_engine():
    return engine


def ensure_pending_signup_table():
    SQLModel.metadata.create_all(engine, tables=[PendingSignup.__table__])

#________________________________________________________________________________________________________________________________________________________

# ------ Pending signup helpers ------

def cleanup_expired_pending_signups(now: Optional[datetime] = None):
    ensure_pending_signup_table()
    cutoff = now or datetime.utcnow()
    with Session(engine) as session:
        expired = session.exec(
            select(PendingSignup).where(PendingSignup.verification_token_expiry < cutoff)
        ).all()
        if not expired:
            return 0
        for row in expired:
            session.delete(row)
        session.commit()
        return len(expired)


def create_or_update_pending_signup(
    email: str,
    password_hash: str,
    first_name: str,
    last_name: str,
    token: str,
    expiry: datetime,
):
    ensure_pending_signup_table()
    first = (first_name or "").strip()
    last = (last_name or "").strip()
    if not first or not last:
        raise ValueError("first_name and last_name must be provided")
    with Session(engine) as session:
        pending = session.exec(select(PendingSignup).where(PendingSignup.email == email)).first()
        if pending:
            pending.password_hash = password_hash
            pending.first_name = first
            pending.last_name = last
            pending.verification_token = token
            pending.verification_token_expiry = expiry
            pending.created_at = datetime.utcnow()
        else:
            pending = PendingSignup(
                email=email,
                password_hash=password_hash,
                first_name=first,
                last_name=last,
                verification_token=token,
                verification_token_expiry=expiry,
            )
        session.add(pending)
        session.commit()
        session.refresh(pending)
        return pending


def get_pending_signup(email: str) -> Optional[PendingSignup]:
    ensure_pending_signup_table()
    with Session(engine) as session:
        return session.exec(select(PendingSignup).where(PendingSignup.email == email)).first()


def delete_pending_signup(email: str) -> bool:
    ensure_pending_signup_table()
    with Session(engine) as session:
        pending = session.exec(select(PendingSignup).where(PendingSignup.email == email)).first()
        if not pending:
            return False
        session.delete(pending)
        session.commit()
        return True


def promote_pending_signup(email: str) -> Optional[Users]:
    ensure_pending_signup_table()
    with Session(engine) as session:
        pending = session.exec(select(PendingSignup).where(PendingSignup.email == email)).first()
        if not pending:
            return None
        existing_user = session.get(Users, email)
        if existing_user:
            session.delete(pending)
            session.commit()
            session.refresh(existing_user)
            return existing_user
        user = Users(
            email=email,
            password_hash=pending.password_hash,
            first_name=pending.first_name,
            last_name=pending.last_name,
        )
        user.is_verified = True
        user.verification_token = None
        user.verification_token_expiry = None
        session.add(user)
        session.delete(pending)
        session.commit()
        session.refresh(user)
        return user


#________________________________________________________________________________________________________________________________________________________

# ------ Users table functions ------

# --- Create User ---

def create_user(email: str, password_hash: str, first_name: str, last_name: str):
    first = (first_name or "").strip()
    last = (last_name or "").strip()
    if not first or not last:
        raise ValueError("first_name and last_name must be provided")
    with Session(engine) as session:
        user = Users(email=email, password_hash=password_hash, first_name=first, last_name=last)
        session.add(user)
        session.commit()


# --- Getters ---

def get_user(email: str) -> Optional[Users]:
    with Session(engine) as session:
        statement = select(Users).where(Users.email == email)
        return session.exec(statement).first()


def get_first_name(email: str) -> Optional[str]:
    user = get_user(email)
    return user.first_name if user else None


def get_last_name(email: str) -> Optional[str]:
    user = get_user(email)
    return user.last_name if user else None

def get_password(email: str) -> Optional[str]:
    user = get_user(email)
    return user.password_hash if user else None

def get_is_admin(email: str) -> Optional[bool]:
    user = get_user(email)
    return user.is_admin if user else None

def get_is_verified(email: str) -> Optional[bool]:
    user = get_user(email)
    return user.is_verified if user else None

def get_verification_token(email: str) -> Optional[str]:
    user = get_user(email)
    return user.verification_token if user else None

def get_verification_token_expiry(email: str) -> Optional[datetime]:
    user = get_user(email)
    return user.verification_token_expiry if user else None

def get_reset_code(email: str) -> Optional[str]:
    user = get_user(email)
    return user.reset_code if user else None

def get_reset_code_expiry(email: str) -> Optional[datetime]:
    user = get_user(email)
    return user.reset_code_expiry if user else None


# --- Setters ---

def update_first_name(email: str, new_first_name: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.first_name = (new_first_name or "").strip()
        session.add(user)
        session.commit()
        session.refresh(user)


def update_last_name(email: str, new_last_name: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.last_name = (new_last_name or "").strip()
        session.add(user)
        session.commit()
        session.refresh(user)

def update_password(email: str, new_password_hash: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.password_hash = new_password_hash
        session.add(user)
        session.commit()
        session.refresh(user)

def update_is_admin(email: str, admin: bool):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.is_admin = admin
        session.add(user)
        session.commit()
        session.refresh(user)

def update_is_verified(email: str, verified: bool):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.is_verified = verified
        session.add(user)
        session.commit()
        session.refresh(user)

def update_verification_token(email: str, token: str, expiry: Optional[datetime] = None):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.verification_token = token
        user.verification_token_expiry = expiry
        session.add(user)
        session.commit()
        session.refresh(user)

def update_reset_code(email: str, code: str, expiry: Optional[datetime] = None):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return None
        user.reset_code = code
        user.reset_code_expiry = expiry
        session.add(user)
        session.commit()
        session.refresh(user)

# --- Delete ---

def delete_user(email: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        session.delete(user)
        session.commit()

#________________________________________________________________________________________________________________________________________________________

# ------ Events table functions ------

# --- Create Event ---

def create_event(
    title: str,
    description: Optional[str] = None,
    date: Optional[datetime] = None,
    location: Optional[str] = None,
    capacity: Optional[int] = None,
    available_seats: Optional[int] = None,
    category: Optional[str] = None,
    created_by: Optional[str] = None,
    image_url: Optional[str] = None
) -> Events:
    
    event = Events(
        title=title,
        description=description,
        date=date,
        location=location,
        capacity=capacity,
        available_seats=available_seats,
        category=category,
        created_by=created_by,
        image_url=image_url
    )

    with Session(get_engine()) as session:
        session.add(event)
        session.commit()
        session.refresh(event)
        return event
    
# --- Getters ---

def get_title(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.title if event else None

def get_description(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.description if event else None
    
def get_organizer(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.organizers if event else None

def get_date(event_id: int) -> Optional[datetime]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.date if event else None

def get_location(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.location if event else None

def get_image_url(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.image_url if event else None

def get_capacity(event_id: int) -> Optional[int]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.capacity if event else None

def get_available_seats(event_id: int) -> Optional[int]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.available_seats if event else None

def get_speakers(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.speakers if event else None

def get_category(event_id: int) -> Optional[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        return event.category if event else None

# --- Setters ---

def update_title(event_id: int, title: str) -> None:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.title = title
        session.add(event)
        session.commit()

def update_description(event_id: int, description: str):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.description = description
        session.add(event)
        session.commit()

def update_organizer(event_id: int, organizer: str) -> None:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return
        event.organizers = organizer
        session.add(event)
        session.commit()

def update_date(event_id: int, date: datetime):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.date = date
        session.add(event)
        session.commit()

def update_location(event_id: int, location: str):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.location = location
        session.add(event)
        session.commit()

def update_image_url(event_id: int, image_url: Optional[str]):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return
        event.image_url = image_url
        session.add(event)
        session.commit()

def update_capacity(event_id: int, capacity: int):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.capacity = capacity
        if event.available_seats is None or event.available_seats > capacity:
            event.available_seats = capacity
        session.add(event)
        session.commit()

def update_available_seats(event_id: int, seats: int):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: 
            return
        event.available_seats = seats
        session.add(event)
        session.commit()

def update_speakers(event_id: int, speakers: str) -> None:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return
        event.speakers = speakers
        session.add(event)
        session.commit()

def update_category(event_id: int, category: Optional[str]) -> None:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return
        event.category = category
        session.add(event)
        session.commit()


# --- Delete ---
def delete_event(event_id: int) -> bool:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return False
        session.delete(event)
        session.commit()
        return True  # ✅ explicitly signal success


#________________________________________________________________________________________________________________________________________________________
# ------ User–Event linking functions ------

def register_user_to_event(user_email: str, event_id: int):
    """
    Register a user to an event with an atomic seat decrement to avoid races.

    Returns (success: bool, reason: Optional[str]) where reason in
    {'full','already_registered','not_found'} on failure.
    """
    with Session(get_engine()) as session:
        # Validate user and event exist first
        user = session.get(Users, user_email)
        if not user:
            return (False, 'not_found')
        event = session.get(Events, event_id)
        if not event:
            return (False, 'not_found')

        # Already registered? quick check via relationship (works fine here)
        if event in user.events:
            return (False, 'already_registered')

        # Initialize available_seats from capacity when missing
        if event.available_seats is None:
            if event.capacity is not None:
                event.available_seats = event.capacity
                session.add(event)
                session.commit()
            else:
                return (False, 'full')

        # Atomic decrement: only decrement when seats > 0
        stmt = (
            update(Events)
            .where(Events.id == event_id, Events.available_seats > 0)
            .values(available_seats=Events.available_seats - 1)
        )
        res = session.exec(stmt)
        # SQLModel's exec returns a Result; use rowcount when available
        try:
            affected = res.rowcount  # type: ignore[attr-defined]
        except Exception:
            # Fallback: treat as no rows when API doesn't expose rowcount
            affected = 0
        if not affected:
            # No seat to take
            return (False, 'full')

        # Link user to event in same transaction
        # Re-fetch event to ensure the instance is attached/updated
        event = session.get(Events, event_id)
        if event in user.events:
            # If link appeared concurrently, nothing to do; keep seat taken
            session.commit()
            return (False, 'already_registered')
        user.events.append(event)
        session.add(user)
        session.commit()
        return (True, None)

def unregister_user_from_event(user_email: str, event_id: int):
    with Session(get_engine()) as session:
        user = session.get(Users, user_email)
        event = session.get(Events, event_id)
        if user and event and event in user.events:
            user.events.remove(event)
            event.available_seats += 1
            session.add(user)
            session.add(event)
            session.commit()
            return True
        return False
def get_user_events(user_email: str, search: Optional[str] = None) -> list[int]:
    """Return a list of event dicts the given user is registered for.

    If `search` is provided, filter by title/location/description (case-insensitive substring).
    """
    with Session(get_engine()) as session:
        user = session.get(Users, user_email)
        if not user:
            return []
        # If no search, return all
        if not search:
            return [
                {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": event.date,
                    "location": event.location,
                    "capacity": event.capacity,
                    "available_seats": event.available_seats,
                    "organizers": getattr(event, "organizers", []) or [],
                    "speakers": getattr(event, "speakers", []) or [],
                    "category": getattr(event, "category", None),
                    "image_url": getattr(event, "image_url", None),
                }
                for event in user.events
            ]

        q = search.lower().strip()
        out = []
        for event in user.events:
            title = (event.title or "").lower()
            desc = (event.description or "").lower()
            loc = (event.location or "").lower()
            if q in title or q in desc or q in loc:
                out.append({
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "date": event.date,
                    "location": event.location,
                    "available_seats": event.available_seats,
                    "category": getattr(event, "category", None),
                    "image_url": getattr(event, "image_url", None),
                })
        return out

def get_event_users(event_id: int) -> list[str]:
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event:
            return []
        return [user.email for user in event.users]

#________________________________________________________________________________________________________________________________________________________
# ------ Testing functions ------

# This function prints all events in the database in a formatted table. Used for testing purposes.
def print_all_events():
    with Session(get_engine()) as session:
        events = session.exec(select(Events)).all()
        if not events:
            print("No events found.")
            return

        print(f"{'ID':<3} | {'Title':<50}")
        print(f"{'-'*3}-|{'-'*50}")

        for event in events:
            print(f"{event.id:<3} | {event.title:<50}")

# List all events
def list_events(search: Optional[str] = None) -> List[Events]:
    """Return events; if search provided, filter by title/location/description (case-insensitive).
    Uses SQL-level filtering when possible.
    """
    with Session(get_engine()) as session:
        if not search:
            return session.exec(select(Events)).all()
        pattern = f"%{search}%"
        stmt = select(Events).where(
            or_(
                Events.title.ilike(pattern),
                Events.description.ilike(pattern),
                Events.location.ilike(pattern),
            )
        )
        return session.exec(stmt).all()
