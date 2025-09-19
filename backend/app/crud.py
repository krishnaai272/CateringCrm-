from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from . import models, schemas
from .auth import get_password_hash
import os
from typing import Optional, List

# -------------------------
# User CRUD
# -------------------------
async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_user_by_username(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreateSchema) -> models.User:
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
async def create_lead(db: AsyncSession, lead: schemas.LeadCreateSchema) -> models.Lead:
    new_lead = models.Lead(**lead.dict())
    db.add(new_lead)
    await db.commit()
    await db.refresh(new_lead)
    return new_lead

async def get_leads(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.Lead]:
    result = await db.execute(select(models.Lead).offset(skip).limit(limit))
    return result.scalars().all()

async def get_lead(db: AsyncSession, lead_id: int) -> Optional[models.Lead]:
    result = await db.execute(select(models.Lead).where(models.Lead.id == lead_id))
    return result.scalar_one_or_none()

async def update_lead(db: AsyncSession, lead_id: int, lead: schemas.LeadUpdateSchema) -> Optional[models.Lead]:
    db_lead = await get_lead(db, lead_id)
    if not db_lead:
        return None
    update_data = lead.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_lead, key, value)
    await db.commit()
    await db.refresh(db_lead)
    return db_lead

async def delete_lead(db: AsyncSession, lead_id: int) -> Optional[models.Lead]:
    db_lead = await db.get(models.Lead, lead_id)
    if db_lead:
        await db.delete(db_lead)
        await db.commit()
        return db_lead
    return None

# -------------------------
# Activity CRUD
# -------------------------
async def create_lead_activity(db: AsyncSession, activity: schemas.ActivityCreateSchema, lead_id: int) -> models.Activity:
    db_activity = models.Activity(**activity.dict(), lead_id=lead_id)
    db.add(db_activity)
    await db.commit()
    await db.refresh(db_activity)
    return db_activity

async def get_lead_activities(db: AsyncSession, lead_id: int) -> List[models.Activity]:
    result = await db.execute(select(models.Activity).where(models.Activity.lead_id == lead_id))
    return result.scalars().all()

# -------------------------
# FollowUp CRUD
# -------------------------
async def create_lead_followup(db: AsyncSession, followup: schemas.FollowUpCreateSchema, lead_id: int) -> models.FollowUp:
    db_followup = models.FollowUp(**followup.dict(), lead_id=lead_id)
    db.add(db_followup)
    await db.commit()
    await db.refresh(db_followup)
    return db_followup

async def get_lead_followups(db: AsyncSession, lead_id: int) -> List[models.FollowUp]:
    result = await db.execute(select(models.FollowUp).where(models.FollowUp.lead_id == lead_id))
    return result.scalars().all()

# -------------------------
# Attachment CRUD
# -------------------------
async def delete_attachment(db: AsyncSession, attachment_id: int) -> Optional[models.Attachment]:
    db_attachment = await db.get(models.Attachment, attachment_id)
    if db_attachment:
        # Delete physical file
        if os.path.exists(db_attachment.file_path):
            try:
                os.remove(db_attachment.file_path)
            except OSError as e:
                print(f"Error deleting file {db_attachment.file_path}: {e}")
        # Delete DB record
        await db.delete(db_attachment)
        await db.commit()
        return db_attachment
    return None