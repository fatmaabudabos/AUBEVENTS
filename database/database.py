
from sqlmodel import Session, select, create_engine
from .tables import Users
from typing import Optional
from datetime import datetime
from .DB_Password import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

def get_engine():
    return engine

# --- Create User ---
def create_user(email: str, password_hash: str):
    with Session(engine) as session:
        user = Users(email=email, password_hash=password_hash, is_verified=False)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

# --- Getters ---
def get_user(email: str) -> Optional[Users]:
    with Session(engine) as session:
        return session.exec(select(Users).where(Users.email == email)).first()

def get_password(email: str) -> Optional[str]:
    u = get_user(email)
    return u.password_hash if u else None

def get_is_admin(email: str) -> Optional[bool]:
    u = get_user(email)
    return u.is_admin if u else None

def get_is_verified(email: str) -> bool:
    u = get_user(email)
    return bool(u and u.is_verified)

def get_verification_token(email: str) -> Optional[str]:
    u = get_user(email)
    return u.verification_token if u else None

def get_verification_token_expiry(email: str) -> Optional[datetime]:
    u = get_user(email)
    return u.verification_token_expiry if u else None

def get_reset_code(email: str) -> Optional[str]:
    u = get_user(email)
    return u.reset_code if u else None

def get_reset_code_expiry(email: str) -> Optional[datetime]:
    u = get_user(email)
    return u.reset_code_expiry if u else None

# --- Setters ---
def update_password(email: str, new_password_hash: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        user.password_hash = new_password_hash
        session.add(user)
        session.commit()
        return True

def update_is_admin(email: str, admin: bool):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        user.is_admin = admin
        session.add(user)
        session.commit()
        return True

def update_is_verified(email: str, verified: bool):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        user.is_verified = verified
        session.add(user)
        session.commit()
        return True

def update_verification_token(email: str, token: Optional[str], expiry: Optional[datetime]):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        user.verification_token = token
        user.verification_token_expiry = expiry
        session.add(user)
        session.commit()
        return True

def update_reset_code(email: str, code: Optional[str], expiry: Optional[datetime]):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        user.reset_code = code
        user.reset_code_expiry = expiry
        session.add(user)
        session.commit()
        return True

# --- Delete ---
def delete_user(email: str):
    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.email == email)).first()
        if not user:
            return False
        session.delete(user)
        session.commit()
        return True


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
