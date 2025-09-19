from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
from typing import List
from app import models, schemas, crud 


from .. import crud, schemas
from ..db import get_db
from ..auth import create_access_token, verify_password
from ..config import settings

router = APIRouter()

# --- AUTHENTICATION ENDPOINT ---



@router.post("/auth/login", response_model=schemas.TokenSchema, tags=["Authentication"])
async def login_for_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    # Authenticate user
    user = await crud.get_user_by_username(db, username=form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    # Create token
    access_token = "some_generated_token"

    # Return Pydantic schema
    return schemas.TokenSchema(access_token=access_token)

# --- USER ENDPOINTS ---
@router.post("/users/", response_model=schemas.UserRead, tags=["Users"])
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return await crud.create_user(db=db, user=user)

@router.get("/users/", response_model=List[schemas.UserReadSchema], tags=["Leads"])
async def read_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db, skip=skip, limit=limit)

# --- LEAD ENDPOINTS ---
@router.post("/leads/", response_model=schemas.LeadRead, tags=["Leads"])
async def create_new_lead(lead: schemas.LeadCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead(db=db, lead=lead)

@router.get("/leads/", response_model=List[schemas.LeadRead], tags=["Leads"])
async def read_all_leads(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await crud.get_leads(db, skip=skip, limit=limit)

@router.get("/leads/{lead_id}", response_model=schemas.LeadRead, tags=["Leads"])
async def read_single_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    db_lead = await crud.get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@router.patch("/leads/{lead_id}", response_model=schemas.LeadRead, tags=["Leads"])
async def update_existing_lead(lead_id: int, lead: schemas.LeadUpdate, db: AsyncSession = Depends(get_db)):
    db_lead = await crud.update_lead(db=db, lead_id=lead_id, lead=lead)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

# Endpoint for just updating the stage, as used by your Streamlit app
@router.patch("/leads/{lead_id}/stage", response_model=schemas.LeadRead, tags=["Leads"])
async def update_lead_stage(lead_id: int, stage_update: schemas.LeadUpdate, db: AsyncSession = Depends(get_db)):
    db_lead = await crud.update_lead(db=db, lead_id=lead_id, lead=stage_update)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

# --- ACTIVITY ENDPOINTS (NESTED UNDER LEADS) ---
@router.post("/leads/{lead_id}/activities/", response_model=schemas.ActivityRead, tags=["Activities"])
async def create_activity_for_lead(lead_id: int, activity: schemas.ActivityCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead_activity(db=db, activity=activity, lead_id=lead_id)

@router.get("/leads/{lead_id}/activities/", response_model=List[schemas.ActivityRead], tags=["Activities"])
async def read_lead_activities(lead_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_lead_activities(db=db, lead_id=lead_id)

# --- FOLLOW-UP ENDPOINTS (NESTED UNDER LEADS) ---
@router.post("/leads/{lead_id}/followups/", response_model=schemas.FollowUpRead, tags=["Follow-ups"])
async def create_followup_for_lead(lead_id: int, followup: schemas.FollowUpCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_lead_followup(db=db, followup=followup, lead_id=lead_id)

@router.get("/leads/{lead_id}/followups/", response_model=List[schemas.FollowUpRead], tags=["Follow-ups"])
async def read_lead_followups(lead_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.get_lead_followups(db=db, lead_id=lead_id)

@router.delete("/leads/{lead_id}", tags=["Leads"])
async def delete_single_lead(lead_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes a lead by its ID.
    """
    # Call the new CRUD function to delete the lead from the database
    deleted_lead = await crud.delete_lead(db=db, lead_id=lead_id)
    
    # If the crud function returned None, it means the lead was not found
    if deleted_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    # If successful, return the message your test case expects
    return {"message": "Lead deleted successfully"}

@router.delete("/attachments/{attachment_id}", tags=["Attachments"])
async def delete_single_attachment(attachment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Deletes an attachment by its ID.
    """
    # Call the CRUD function to delete the attachment from the DB and filesystem
    deleted_attachment = await crud.delete_attachment(db=db, attachment_id=attachment_id)
    
    # If the attachment was not found, raise a 404 error
    if deleted_attachment is None:
        raise HTTPException(status_code=404, detail="Attachment not found")
        
    # If successful, return a success message
    return {"message": "Attachment deleted successfully"}



