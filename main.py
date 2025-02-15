import os
import shutil
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Header
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from pydantic import BaseModel, validator

DATABASE_URL = (
    f"postgresql://{os.environ.get('POSTGRES_USER', 'postgres')}:"
    f"{os.environ.get('POSTGRES_PASSWORD', 'postgres')}@db:5432/"
    f"{os.environ.get('POSTGRES_DB', 'alltrails')}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Trail(Base):
    __tablename__ = "trails"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    length = Column(Float, nullable=False) # km
    duration = Column(Integer, nullable=False)  # minutes
    elevation_gain = Column(Integer, nullable=False)
    type = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

class TrailBase(BaseModel):
    name: str
    location: str
    difficulty: str
    length: float
    duration: int
    elevation_gain: int
    type: str

    @validator('type', pre=True, always=True)
    def validate_and_format_type(cls, v):
        if not isinstance(v, str):
            raise ValueError('type must be a string')
        v_lower = v.lower()
        mapping = {
            "circular": "Circular",
            "out-and-back": "Out-and-back",
            "point to point": "Point To Point"
        }
        if v_lower in mapping:
            return mapping[v_lower]
        raise ValueError(f"Invalid Type '{v}'. Allowed Types: {', '.join(mapping.keys())}")
    
    @validator('difficulty', pre=True, always=True)
    def validate_and_format_difficulty(cls, v):
        if not isinstance(v, str):
            raise ValueError('type must be a string')
        v_lower = v.lower()
        mapping = {
            "easy": "Easy",
            "moderate": "Moderate",
            "hard": "Hard"
        }
        if v_lower in mapping:
            return mapping[v_lower]
        raise ValueError(f"Invalid Difficulty '{v}'. Allowed Difficulties: {', '.join(mapping.keys())}")

class TrailCreate(TrailBase):
    pass

class TrailUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    difficulty: Optional[str] = None
    length: Optional[float] = None
    duration: Optional[int] = None
    elevation_gain: Optional[int] = None
    type: Optional[str] = None

    @validator('type', pre=True, always=True)
    def validate_and_format_type(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError('type must be a string')
        v_lower = v.lower()
        mapping = {
            "circular": "Circular",
            "out-and-back": "Out-and-back",
            "point to point": "Point To Point"
        }
        if v_lower in mapping:
            return mapping[v_lower]
        raise ValueError(f"Invalid Type '{v}'. Allowed Types: {', '.join(mapping.keys())}")
    
    @validator('difficulty', pre=True, always=True)
    def validate_and_format_difficulty(cls, v):
        if v is None:
            return v
        if not isinstance(v, str):
            raise ValueError('type must be a string')
        v_lower = v.lower()
        mapping = {
            "easy": "Easy",
            "moderate": "Moderate",
            "hard": "Hard"
        }
        if v_lower in mapping:
            return mapping[v_lower]
        raise ValueError(f"Invalid Difficulty '{v}'. Allowed Difficulties: {', '.join(mapping.keys())}")

class TrailOut(TrailBase):
    id: int
    cover_photo: Optional[str] = None

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Fake AllTrails API")

# Pre-load fake trails
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(Trail).count() == 0:
        fake_trails = [
            {
                "name": "Sunny Trail",
                "location": "Mountain View",
                "difficulty": "Easy",
                "length": 3.5,
                "duration": 60,
                "elevation_gain": 200,
                "type": "Circular"
            },
            {
                "name": "Rocky Path",
                "location": "Boulder",
                "difficulty": "Hard",
                "length": 5.0,
                "duration": 120,
                "elevation_gain": 500,
                "type": "Out-and-back"
            },
            {
                "name": "Forest Run",
                "location": "Redwood",
                "difficulty": "Moderate",
                "length": 4.2,
                "duration": 90,
                "elevation_gain": 300,
                "type": "Point To Point"
            },
        ]
        for data in fake_trails:
            trail = Trail(**data)
            db.add(trail)
        db.commit()
    db.close()

@app.get("/trails", response_model=List[TrailOut])
def read_trails(difficulty: Optional[str] = None, sortBy: Optional[str] = None, count: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Trail)
    if difficulty:
        query = query.filter(Trail.difficulty == difficulty)
    if sortBy:
        if not hasattr(Trail, sortBy):
            raise HTTPException(status_code=400, detail="Invalid sortBy parameter")
        query = query.order_by(getattr(Trail, sortBy))
    if count:
        query = query.limit(count)
    return query.all()

@app.get("/trails/{trail_id}", response_model=TrailOut)
def get_trail(trail_id: int, db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id).first()
    if not trail:
        raise HTTPException(status_code=404, detail="Trail not found")
    return trail

@app.post("/trails", response_model=TrailOut, status_code=201)
def create_trail(trail: TrailCreate, db: Session = Depends(get_db)):
    new_trail = Trail(**trail.dict())
    db.add(new_trail)
    db.commit()
    db.refresh(new_trail)
    return new_trail

# This route is idempotent: updating with the same data always returns the same result.
@app.put("/trails/{trail_id}", response_model=TrailOut)
def update_trail(trail_id: int, trail_update: TrailUpdate, db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id).first()
    if not trail:
        raise HTTPException(status_code=404, detail="Trail not found")
    update_data = trail_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trail, key, value)
    db.commit()
    db.refresh(trail)
    return trail

# This is idempotent because deleting an already-deleted trail results in a 404.
@app.delete("/trails/{trail_id}", status_code=204)
def delete_trail(trail_id: int, db: Session = Depends(get_db)):
    trail = db.query(Trail).filter(Trail.id == trail_id).first()
    if not trail:
        raise HTTPException(status_code=404, detail="Trail not found")
    db.delete(trail)
    db.commit()
    return

# DELETE /trails (batch delete)
# Deletes all trails that match the given condition (e.g. difficulty).
# This route requires an admin token in the request header (X-Admin-Token).
@app.delete("/trails", status_code=204)
def batch_delete_trails(
    difficulty: Optional[str] = None,
    admin_token: str = Header(None, alias="X-Admin-Token"),
    db: Session = Depends(get_db)
):
    if admin_token != "secret-admin-token":
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(Trail)
    if difficulty:
        query = query.filter(Trail.difficulty == difficulty)
    trails = query.all()
    if not trails:
        raise HTTPException(status_code=404, detail="No trails match the given condition")
    for trail in trails:
        db.delete(trail)
    db.commit()
    return