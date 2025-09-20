from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime
from database import SessionLocal
from sqlalchemy.orm import Session
import whatsapp_service
import queue

# Create a global queue for message tasks
message_queue = queue.Queue()

# Configure scheduler for sequential execution
scheduler = BackgroundScheduler({
    'apscheduler.job_defaults.max_instances': 1,  # Only one instance of a job at a time
    'apscheduler.executors.default': {
        'class': 'apscheduler.executors.pool:ThreadPoolExecutor',
        'max_workers': 1  # Single thread for jobs
    }
})

def get_db_session():
    """Create a new database session"""
    return SessionLocal()

def send_scheduled_message(schedule_id):
    """Send a scheduled message and update status"""
    db = get_db_session()
    try:
        from models import Schedule, MessageHistory
        
        schedule = db.query(Schedule).filter(Schedule.id == schedule_id).first()
        
        if not schedule:
            return
        
        # Send the message using shared profile
        success = whatsapp_service.send_whatsapp_with_retry(schedule.phone, schedule.message)
        
        if success:
            schedule.status = "sent"
            history = MessageHistory(
                phone=schedule.phone,
                message=schedule.message,
                status="sent",
                sent_at=datetime.utcnow()
            )
            db.add(history)
        else:
            schedule.status = "failed"
            history = MessageHistory(
                phone=schedule.phone,
                message=schedule.message,
                status="failed",
                sent_at=datetime.utcnow()
            )
            db.add(history)
        
        schedule.sent_at = datetime.utcnow()
        db.commit()
        
    except Exception as e:
        print(f"Error sending scheduled message: {e}")
        if schedule:
            schedule.status = "failed"
            db.commit()
    finally:
        db.close()

def schedule_message(schedule_id, run_time):
    """Schedule a message to be enqueued at a specific time"""
    scheduler.add_job(
        lambda: message_queue.put(schedule_id),
        trigger=DateTrigger(run_date=run_time),
        id=f"schedule_{schedule_id}",
        max_instances=1
    )

def init_scheduler():
    """Initialize scheduler with pending messages on startup"""
    db = get_db_session()
    try:
        from models import Schedule
        
        pending_schedules = db.query(Schedule).filter(
            Schedule.status == "pending"
        ).all()
        
        for schedule in pending_schedules:
            if schedule.scheduled_time > datetime.utcnow():
                schedule_message(schedule.id, schedule.scheduled_time)
            else:
                message_queue.put(schedule.id)
    finally:
        db.close()

# Start the scheduler
scheduler.start()