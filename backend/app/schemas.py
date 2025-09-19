from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String


 

# -------------------------
# ORM Models
# -------------------------
class Token(Base):
    __tablename__ = "tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    access_token: Mapped[str] = mapped_column(String(255))


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[Optional[str]] = mapped_column(String(50), default="Staff")
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    event_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    guests_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    event_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    venue: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stage: Mapped[str] = mapped_column(String(50), default="New")
    created_by: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FollowUp(Base):
    __tablename__ = "followups"

    id: Mapped[int] = mapped_column(primary_key=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id"), nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="Pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

# -------------------------
# Pydantic Schemas
# -------------------------
# Users
class UserBaseSchema(BaseModel):
    username: str
    full_name: Optional[str] = None
    role: Optional[str] = "Staff"

class UserCreateSchema(UserBaseSchema):
    password: str

class UserReadSchema(UserBaseSchema):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Leads
class LeadBaseSchema(BaseModel):
    name: str
    phone: str
    email: Optional[EmailStr] = None
    event_type: Optional[str] = None
    guests_count: Optional[int] = None
    event_date: Optional[date] = None
    venue: Optional[str] = None
    notes: Optional[str] = None

class LeadCreateSchema(LeadBaseSchema):
    created_by: Optional[int] = None

class LeadUpdateSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    event_type: Optional[str] = None
    guests_count: Optional[int] = None
    event_date: Optional[date] = None
    venue: Optional[str] = None
    notes: Optional[str] = None
    stage: Optional[str] = None

class LeadReadSchema(LeadBaseSchema):
    id: int
    stage: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

# Activities
class ActivityBaseSchema(BaseModel):
    type: str
    content: Optional[str] = None

class ActivityCreateSchema(ActivityBaseSchema):
    user_id: Optional[int] = None

class ActivityReadSchema(ActivityBaseSchema):
    id: int
    lead_id: int
    user_id: Optional[int] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# FollowUps
class FollowUpBaseSchema(BaseModel):
    scheduled_at: datetime
    note: Optional[str] = None

class FollowUpCreateSchema(FollowUpBaseSchema):
    user_id: Optional[int] = None

class FollowUpReadSchema(FollowUpBaseSchema):
    id: int
    lead_id: int
    user_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True