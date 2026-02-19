"""
Database configuration and models for the extracurricular activities system.
Using SQLite with SQLAlchemy ORM for data persistence.
"""

import json
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, List
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, List as ListType

# Database configuration
DATABASE_URL = "sqlite:///./activities.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite requirement
    echo=False  # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Activity(Base):
    """Database model for an activity"""
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String)
    schedule = Column(String)
    max_participants = Column(Integer)
    participants_json = Column(String, default="[]")  # Store as JSON string

    def get_participants(self) -> ListType[str]:
        """Parse and return participants list"""
        return json.loads(self.participants_json)

    def set_participants(self, participants: ListType[str]):
        """Store participants as JSON string"""
        self.participants_json = json.dumps(participants)

    def to_dict(self) -> Dict:
        """Convert to dictionary format for API responses"""
        return {
            "description": self.description,
            "schedule": self.schedule,
            "max_participants": self.max_participants,
            "participants": self.get_participants()
        }


def init_db():
    """Initialize database and seed with default activities"""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if activities already exist
        if db.query(Activity).count() > 0:
            return

        # Default activities to seed
        default_activities = [
            {
                "name": "Chess Club",
                "description": "Learn strategies and compete in chess tournaments",
                "schedule": "Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 12,
                "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
            },
            {
                "name": "Programming Class",
                "description": "Learn programming fundamentals and build software projects",
                "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
                "max_participants": 20,
                "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
            },
            {
                "name": "Gym Class",
                "description": "Physical education and sports activities",
                "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
                "max_participants": 30,
                "participants": ["john@mergington.edu", "olivia@mergington.edu"]
            },
            {
                "name": "Soccer Team",
                "description": "Join the school soccer team and compete in matches",
                "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
                "max_participants": 22,
                "participants": ["liam@mergington.edu", "noah@mergington.edu"]
            },
            {
                "name": "Basketball Team",
                "description": "Practice and play basketball with the school team",
                "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["ava@mergington.edu", "mia@mergington.edu"]
            },
            {
                "name": "Art Club",
                "description": "Explore your creativity through painting and drawing",
                "schedule": "Thursdays, 3:30 PM - 5:00 PM",
                "max_participants": 15,
                "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
            },
            {
                "name": "Drama Club",
                "description": "Act, direct, and produce plays and performances",
                "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
                "max_participants": 20,
                "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
            },
            {
                "name": "Math Club",
                "description": "Solve challenging problems and participate in math competitions",
                "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
                "max_participants": 10,
                "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
            },
            {
                "name": "Debate Team",
                "description": "Develop public speaking and argumentation skills",
                "schedule": "Fridays, 4:00 PM - 5:30 PM",
                "max_participants": 12,
                "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
            }
        ]

        # Add activities to database
        for activity_data in default_activities:
            activity = Activity(
                name=activity_data["name"],
                description=activity_data["description"],
                schedule=activity_data["schedule"],
                max_participants=activity_data["max_participants"]
            )
            activity.set_participants(activity_data["participants"])
            db.add(activity)

        db.commit()
    finally:
        db.close()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
