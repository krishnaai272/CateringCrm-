from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey, JSON, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, declarative_base
from .db import Base




# -------------------------
# User Model
# -------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="Staff")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    leads = relationship("Lead", back_populates="creator", cascade="all, delete")
    activities = relationship("Activity", back_populates="user", cascade="all, delete")
    followups = relationship("FollowUp", back_populates="user", cascade="all, delete")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete")


# -------------------------
# Lead Model
# -------------------------
class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255))
    event_type = Column(String(50))
    guests_count = Column(Integer)
    event_date = Column(Date)
    venue = Column(String(255))
    notes = Column(Text)
    stage = Column(String(50), default="New", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    # Relationships
    creator = relationship("User", back_populates="leads")
    activities = relationship("Activity", back_populates="lead", cascade="all, delete")
    followups = relationship("FollowUp", back_populates="lead", cascade="all, delete")


# -------------------------
# Activity Model
# -------------------------
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50))
    content = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    user = relationship("User", back_populates="activities")


# -------------------------
# FollowUp Model
# -------------------------
class FollowUp(Base):
    __tablename__ = "followups"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    scheduled_at = Column(DateTime(timezone=True))
    note = Column(Text)
    status = Column(String(20), default="pending")  # pending | done | overdue
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="followups")
    user = relationship("User", back_populates="followups")


# -------------------------
# AuditLog Model
# -------------------------
class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(255))
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")


# -------------------------
# Indexes for performance
# -------------------------
Index("ix_leads_event_date", Lead.event_date)
Index("ix_leads_stage", Lead.stage)
Index("ix_leads_created_at", Lead.created_at)