from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(String(255))

# -------------------------
# User Schemas
# -------------------------


class UserBase(Base):
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "Staff"

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# -------------------------
# Lead Schemas
# -------------------------
class LeadBase(Base):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    event_type: Optional[str] = None
    guests_count: Optional[int] = None
    event_date: Optional[date] = None
    venue: Optional[str] = None
    notes: Optional[str] = None

class LeadCreate(LeadBase):
    created_by: Optional[int] = None

class LeadUpdate(Base):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    event_type: Optional[str] = None
    guests_count: Optional[int] = None
    event_date: Optional[date] = None
    venue: Optional[str] = None
    notes: Optional[str] = None
    stage: Optional[str] = None

class LeadRead(LeadBase):
    id: int
    stage: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# -------------------------
# Activity Schemas
# -------------------------
class ActivityBase(Base):
    type: str
    content: Optional[str] = None

class ActivityCreate(ActivityBase):
    user_id: Optional[int] = None

class ActivityRead(ActivityBase):
    id: int
    lead_id: int
    user_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# -------------------------
# FollowUp Schemas
# -------------------------
class FollowUpBase(Base):
    scheduled_at: datetime
    note: Optional[str] = None

class FollowUpCreate(FollowUpBase):
    user_id: Optional[int] = None

class FollowUpRead(FollowUpBase):
    id: int
    lead_id: int
    user_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True