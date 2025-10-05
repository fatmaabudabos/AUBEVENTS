# List of database functions to be used in the backend

from sqlmodel import Session, select, create_engine
from database.tables import Users
from database.tables import Events
from typing import Optional, List
from datetime import datetime
from database.DB_Password import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False)

def get_engine():
    return engine

#________________________________________________________________________________________________________________________________________________________

# ------ Users table functions ------

# --- Create User ---

def create_user(email: str, password_hash: str):
    with Session(engine) as session:
        user = Users(email=email, password_hash=password_hash)
        session.add(user)
        session.commit()


# --- Getters ---

def get_user(email: str) -> Optional[Users]:
    with Session(engine) as session:
        statement = select(Users).where(Users.email == email)
        return session.exec(statement).first()

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
    available_seats: Optional[int] = None
) -> Events:
    
    event = Events(
        title=title,
        description=description,
        date=date,
        location=location,
        capacity=capacity,
        available_seats=available_seats
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


# --- Delete ---

def delete_event(event_id: int):
    with Session(get_engine()) as session:
        event = session.get(Events, event_id)
        if not event: return False
        session.delete(event)
        session.commit()

#________________________________________________________________________________________________________________________________________________________
# ------ User–Event linking functions ------

def register_user_to_event(user_email: str, event_id: int):
    with Session(get_engine()) as session:
        user = session.get(Users, user_email)
        event = session.get(Events, event_id)
        if user and event:
            if event not in user.events:
                user.events.append(event)
                session.add(user)
                session.commit()

def unregister_user_from_event(user_email: str, event_id: int):
    with Session(get_engine()) as session:
        user = session.get(Users, user_email)
        event = session.get(Events, event_id)
        if user and event and event in user.events:
            user.events.remove(event)
            session.add(user)
            session.commit()

def get_user_events(user_email: str) -> list[int]:
    with Session(get_engine()) as session:
        user = session.get(Users, user_email)
        if not user:
            return []
        return [event.id for event in user.events]

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
def list_events() -> List[Events]:
    with Session(get_engine()) as session:
        return session.exec(select(Events)).all()
