from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from . import models, schemas
from .auth import get_password_hash
from typing import Optional
import os

# -------------------------
# User CRUD
# -------------------------
async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreateSchema):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# -------------------------
# Lead CRUD
# -------------------------
async def create_lead(db: AsyncSession, lead: schemas.LeadCreateSchema):
    new_lead = models.Lead(**lead.dict())
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

async def get_leads(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(models.Lead).offset(skip).limit(limit))
    return result.scalars().all()

async def get_lead(db: AsyncSession, lead_id: int):
    result = await db.execute(select(models.Lead).where(models.Lead.id == lead_id))
    return result.scalar_one_or_none()

async def update_lead(db: AsyncSession, lead_id: int, lead: schemas.LeadUpdateSchema):
    db_lead = await get_lead(db, lead_id)
    if not db_lead:
        return None
    update_data = lead.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead

# -------------------------
# Activity CRUD
# -------------------------
async def create_lead_activity(db: AsyncSession, activity: schemas.ActivityCreateSchema, lead_id: int):
    db_activity = models.Activity(**activity.dict(), lead_id=lead_id)
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity

async def get_lead_activities(db: AsyncSession, lead_id: int):
    result = await db.execute(select(models.Activity).where(models.Activity.lead_id == lead_id))
    return result.scalars().all()

# -------------------------
# FollowUp CRUD
# -------------------------
async def create_lead_followup(db: AsyncSession, followup: schemas.FollowUpCreateSchema, lead_id: int):
    db_followup = models.FollowUp(**followup.dict(), lead_id=lead_id)
    db.add(db_followup)
    await db.commit()
    await db.refresh(db_followup)
    return db_followup

async def get_lead_followups(db: AsyncSession, lead_id: int):
    result = await db.execute(select(models.FollowUp).where(models.FollowUp.lead_id == lead_id))
    return result.scalars().all()