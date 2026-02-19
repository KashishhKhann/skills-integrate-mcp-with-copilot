"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.

Uses SQLite persistent database for data durability and multi-user support.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path
from sqlalchemy.orm import Session

from database import init_db, get_db, Activity

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")


@app.on_event("startup")
def startup_event():
    """Initialize database on app startup"""
    init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities(db: Session = Depends(get_db)):
    """Retrieve all activities from the database"""
    activities = db.query(Activity).all()
    return {activity.name: activity.to_dict() for activity in activities}


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Sign up a student for an activity"""
    # Query activity from database
    activity = db.query(Activity).filter(Activity.name == activity_name).first()

    # Validate activity exists
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get participants list
    participants = activity.get_participants()

    # Validate student is not already signed up
    if email in participants:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Check capacity
    if len(participants) >= activity.max_participants:
        raise HTTPException(
            status_code=400,
            detail="Activity is at maximum capacity"
        )

    # Add student
    participants.append(email)
    activity.set_participants(participants)
    db.commit()

    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str, db: Session = Depends(get_db)):
    """Unregister a student from an activity"""
    # Query activity from database
    activity = db.query(Activity).filter(Activity.name == activity_name).first()

    # Validate activity exists
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get participants list
    participants = activity.get_participants()

    # Validate student is signed up
    if email not in participants:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    participants.remove(email)
    activity.set_participants(participants)
    db.commit()

    return {"message": f"Unregistered {email} from {activity_name}"}
