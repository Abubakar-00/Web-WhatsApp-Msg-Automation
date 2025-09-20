from fastapi import FastAPI, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, date
from database import Base, engine, get_db
from scheduler import init_scheduler, schedule_message, send_scheduled_message, message_queue
import models
import threading
import queue
import whatsapp_service

app = FastAPI(title="WhatsApp Automation API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Create database tables
Base.metadata.create_all(bind=engine)

def message_worker():
    """Worker thread to process messages from the queue sequentially"""
    while True:
        try:
            # Get next task from queue (blocks until a task is available)
            schedule_id = message_queue.get()
            print(f"Processing message for schedule ID: {schedule_id}")
            send_scheduled_message(schedule_id)
            message_queue.task_done()
        except Exception as e:
            print(f"Error in message worker: {e}")

@app.on_event("startup")
async def startup_event():
    """Initialize scheduler and message worker on startup"""
    init_scheduler()
    # Start the message worker thread
    worker_thread = threading.Thread(target=message_worker, daemon=True)
    worker_thread.start()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    """Render the main dashboard"""
    pending_schedules = db.query(models.Schedule).filter(
        models.Schedule.status == "pending"
    ).order_by(models.Schedule.scheduled_time).all()
    
    message_history = db.query(models.MessageHistory).order_by(
        models.MessageHistory.sent_at.desc()
    ).limit(50).all()

    # Compute dashboard stats
    pending_count = len(pending_schedules)
    
    today = date.today()
    sent_today_count = len([
        h for h in message_history 
        if h.sent_at.date() == today and h.status == 'sent'
    ])
    
    failed_count = len([
        h for h in message_history 
        if h.status == 'failed'
    ])
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "pending_schedules": pending_schedules,
        "message_history": message_history,
        "pending_count": pending_count,
        "sent_today_count": sent_today_count,
        "failed_count": failed_count
    })

@app.post("/schedules")
async def create_schedule(
    request: Request,
    phone: str = Form(...),
    message: str = Form(...),
    schedule_type: str = Form(...),
    scheduled_time: str = Form(None),
    db: Session = Depends(get_db)
):
    """Create a new message schedule"""
    try:
        if schedule_type == "now":
            is_immediate = True
            scheduled_dt = datetime.utcnow()
        else:
            is_immediate = False
            if not scheduled_time:
                raise HTTPException(status_code=400, detail="Scheduled time is required")
            
            scheduled_dt = datetime.fromisoformat(scheduled_time.replace("Z", "+00:00"))
        
        schedule = models.Schedule(
            phone=phone,
            message=message,
            scheduled_time=scheduled_dt,
            is_immediate=is_immediate,
            status="pending"
        )
        
        db.add(schedule)
        db.commit()
        db.refresh(schedule)
        
        if is_immediate:
            # Enqueue immediate send
            message_queue.put(schedule.id)
        else:
            # Schedule for later
            schedule_message(schedule.id, scheduled_dt)
        
        return RedirectResponse(url="/", status_code=303)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/schedules/{schedule_id}/cancel")
async def cancel_schedule(schedule_id: int, db: Session = Depends(get_db)):
    """Cancel a pending schedule"""
    schedule = db.query(models.Schedule).filter(models.Schedule.id == schedule_id).first()
    
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    if schedule.status != "pending":
        raise HTTPException(status_code=400, detail="Only pending schedules can be canceled")
    
    try:
        from scheduler import scheduler
        scheduler.remove_job(f"schedule_{schedule_id}")
    except:
        pass
    
    schedule.status = "canceled"
    db.commit()
    
    return {"message": "Schedule canceled successfully"}

@app.get("/pending-schedules")
async def get_pending_schedules(db: Session = Depends(get_db)):
    """Get pending schedules as JSON"""
    pending_schedules = db.query(models.Schedule).filter(
        models.Schedule.status == "pending"
    ).order_by(models.Schedule.scheduled_time).all()
    
    schedules_data = [
        {
            "id": schedule.id,
            "phone": schedule.phone,
            "message": schedule.message[:50] + ("..." if len(schedule.message) > 50 else ""),
            "scheduled_time": (
                "Immediately" if schedule.is_immediate
                else schedule.scheduled_time.strftime("%Y-%m-%d %H:%M")
            ),
            "status": schedule.status
        }
        for schedule in pending_schedules
    ]
    
    return schedules_data

@app.get("/message-history")
async def get_message_history(db: Session = Depends(get_db)):
    """Get message history"""
    history = db.query(models.MessageHistory).order_by(
        models.MessageHistory.sent_at.desc()
    ).all()
    
    return history

@app.post("/setup-login")
async def setup_login():
    """Setup WhatsApp login"""
    success = whatsapp_service.setup_whatsapp_login()
    
    if success:
        return RedirectResponse(url="/?login_success=true", status_code=303)
    else:
        return RedirectResponse(url="/?login_success=false", status_code=303)

@app.post("/clear-login")
async def clear_login():
    """Clear saved WhatsApp login"""
    whatsapp_service.clear_saved_login()
    return RedirectResponse(url="/?logout_success=true", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)