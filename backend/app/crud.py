from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, delete
from . import models, schemas
from .auth import get_password_hash  # assuming you have this
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

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        full_name=user.full_name,
        password_hash=hashed_password,
        role=user.role
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

# -------------------------
# Lead CRUD
# -------------------------
async def create_lead(db: AsyncSession, lead: schemas.LeadCreate):
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

async def update_lead(db: AsyncSession, lead_id: int, lead: schemas.LeadUpdate):
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
async def create_lead_activity(db: AsyncSession, activity: schemas.ActivityCreate, lead_id: int):
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
async def create_lead_followup(db: AsyncSession, followup: schemas.FollowUpCreate, lead_id: int):
    db_followup = models.FollowUp(**followup.dict(), lead_id=lead_id)
    db.add(db_followup)
    await db.commit()
    await db.refresh(db_followup)
    return db_followup

async def get_lead_followups(db: AsyncSession, lead_id: int):
    result = await db.execute(select(models.FollowUp).where(models.FollowUp.lead_id == lead_id))
    return result.scalars().all()

async def delete_lead(db: AsyncSession, lead_id: int):
    """Deletes a lead from the database by its ID."""
    # Get the lead object by its primary key
    db_lead = await db.get(models.Lead, lead_id)
    
    # If the lead exists, delete it and commit
    if db_lead:
        await db.delete(db_lead)
        await db.commit()
        return db_lead  # Return the deleted object to confirm success
    
async def delete_attachment(db: AsyncSession, attachment_id: int):
    """Deletes an attachment from the database and the filesystem."""
    # Get the attachment object by its primary key
    db_attachment = await db.get(models.Attachment, attachment_id)
    
    if db_attachment:
        # Step 1: Delete the physical file from the server
        if os.path.exists(db_attachment.file_path):
            try:
                os.remove(db_attachment.file_path)
            except OSError as e:
                # Handle potential errors if the file can't be deleted
                print(f"Error deleting file {db_attachment.file_path}: {e}")

        # Step 2: Delete the record from the database
        await db.delete(db_attachment)
        await db.commit()
        return db_attachment  # Return the deleted object to confirm success
    
    return None # Return None if the attachment was not found