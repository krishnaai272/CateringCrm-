from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from .. import crud, schemas, models
from ..db import get_db
from ..auth import verify_password
from sqlalchemy import select

router = APIRouter()

# -------------------------
# AUTHENTICATION
# -------------------------
@router.post("/auth/login", response_model=schemas.TokenSchema, tags=["Authentication"])
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = "some_generated_token"
    return schemas.TokenSchema(access_token=access_token)

# -------------------------
# USERS
# -------------------------
@router.post("/users/", response_model=schemas.UserReadSchema, tags=["Users"])
async def create_user(user: schemas.UserCreateSchema, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.UserReadSchema], tags=["Users"])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

# -------------------------
# LEADS
# -------------------------
@router.post("/leads/", response_model=schemas.LeadReadSchema, tags=["Leads"])
async def create_new_lead(lead: schemas.LeadCreateSchema, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead(db=db, lead=lead)

@router.get("/leads/", response_model=List[schemas.LeadReadSchema], tags=["Leads"])
async def read_all_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_leads(db, skip=skip, limit=limit)

@router.get("/leads/{lead_id}", response_model=schemas.LeadReadSchema, tags=["Leads"])
async def read_single_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    db_lead = await crud.get_lead(db, lead_id=lead_id)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.patch("/leads/{lead_id}", response_model=schemas.LeadReadSchema, tags=["Leads"])
async def update_existing_lead(lead_id: int, lead: schemas.LeadUpdateSchema, db: AsyncSession = Depends(get_db)):
    db_lead = await crud.update_lead(db=db, lead_id=lead_id, lead=lead)
    if not db_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

# -------------------------
# ACTIVITY (NESTED UNDER LEADS)
# -------------------------
@router.post("/leads/{lead_id}/activities/", response_model=schemas.ActivityReadSchema, tags=["Activities"])
async def create_activity_for_lead(lead_id: int, activity: schemas.ActivityCreateSchema, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead_activity(db=db, activity=activity, lead_id=lead_id)

@router.get("/leads/{lead_id}/activities/", response_model=List[schemas.ActivityReadSchema], tags=["Activities"])
async def read_lead_activities(lead_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_lead_activities(db=db, lead_id=lead_id)

# -------------------------
# FOLLOW-UPS (NESTED UNDER LEADS)
# -------------------------
@router.post("/leads/{lead_id}/followups/", response_model=schemas.FollowUpReadSchema, tags=["Follow-ups"])
async def create_followup_for_lead(lead_id: int, followup: schemas.FollowUpCreateSchema, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead_followup(db=db, followup=followup, lead_id=lead_id)

@router.get("/leads/{lead_id}/followups/", response_model=List[schemas.FollowUpReadSchema], tags=["Follow-ups"])
async def read_lead_followups(lead_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_lead_followups(db=db, lead_id=lead_id)

# -------------------------
# DELETE ENDPOINTS
# -------------------------
@router.delete("/leads/{lead_id}", tags=["Leads"])
async def delete_single_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    deleted_lead = await crud.delete_lead(db=db, lead_id=lead_id)
    if not deleted_lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"message": "Lead deleted successfully"}

@router.delete("/attachments/{attachment_id}", tags=["Attachments"])
async def delete_single_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    deleted_attachment = await crud.delete_attachment(db=db, attachment_id=attachment_id)
    if not deleted_attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    return {"message": "Attachment deleted successfully"}

@router.put("/leads/{lead_id}", response_model=schemas.LeadReadSchema)
async def update_lead(
    lead_id: int,
    lead_update: schemas.LeadUpdateSchema,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(models.Lead).where(models.Lead.id == lead_id))
    lead = result.scalars().first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = lead_update.dict(exclude_unset=True)  # ✅ only update given fields
    for key, value in update_data.items():
        setattr(lead, key, value)

    db.add(lead)
    await db.commit()
    await db.refresh(lead)

    return lead