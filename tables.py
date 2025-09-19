# List of tables for the database

from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Users(SQLModel, table=True):
    email: str = Field(primary_key = True)
    password_hash: str

    is_verified: bool = Field(default=False)
    verification_token: Optional[str] = Field(default=None)
    verification_token_expiry: Optional[datetime] = Field(default=None)

    reset_code: Optional[str] = Field(default=None)
    reset_code_expiry: Optional[datetime] = Field(default=None)