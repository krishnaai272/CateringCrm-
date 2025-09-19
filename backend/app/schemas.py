from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

# -------------------------
# Users
# -------------------------

class TokenSchema(BaseModel):
    access_token: str

    class Config:
        from_attributes = True  # allows reading from SQLAlchemy models if needed

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
        from_attributes = True  # allows ORM -> Pydantic conversion


# -------------------------
# Leads
# -------------------------
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


# -------------------------
# Activities
# -------------------------
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


# -------------------------
# FollowUps
# -------------------------
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