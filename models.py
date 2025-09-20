# models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from database import Base, engine
from datetime import datetime

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)
    message = Column(String, nullable=False)
    scheduled_time = Column(DateTime, default=datetime.utcnow)
    is_immediate = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending, sent, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)

class MessageHistory(Base):
    __tablename__ = "message_history"
    
    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String, nullable=False)
    message = Column(String, nullable=False)
    status = Column(String, default="sent")  # sent, failed
    sent_at = Column(DateTime, default=datetime.utcnow)