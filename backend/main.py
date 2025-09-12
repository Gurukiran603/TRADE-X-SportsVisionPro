from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import jwt
import bcrypt
import os
import uuid
from datetime import datetime, timedelta
import shutil
from pathlib import Path
import subprocess
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./sports_analysis.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Video(Base):
    __tablename__ = "videos"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    original_filename = Column(String)
    processed_filename = Column(String)
    status = Column(String, default="processing")  # processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Integer)  # in seconds

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    phone: str
    password: str
    full_name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    phone: str
    full_name: str
    is_active: bool
    created_at: datetime

class VideoResponse(BaseModel):
    id: int
    original_filename: str
    processed_filename: str
    status: str
    created_at: datetime
    processing_time: Optional[int]

# JWT Configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# FastAPI app
app = FastAPI(title="Sports Video Analysis API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
os.makedirs("uploads", exist_ok=True)
os.makedirs("processed", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/processed", StaticFiles(directory="processed"), name="processed")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Background task executor
executor = ThreadPoolExecutor(max_workers=2)

def process_video_sync(video_id: int, input_path: str, output_path: str):
    """Process video in background thread"""
    try:
        # Import the video processor
        from video_processor import process_video_file
        
        start_time = datetime.now()
        
        # Process the video
        result = process_video_file(
            input_path, 
            output_path, 
            trail_len=30, 
            heatmap=True
        )
        
        end_time = datetime.now()
        processing_time = int((end_time - start_time).total_seconds())
        
        # Update database
        db = SessionLocal()
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            if result['success']:
                video.status = "completed"
                video.processing_time = processing_time
            else:
                video.status = "failed"
            db.commit()
        db.close()
        
    except Exception as e:
        print(f"Error processing video {video_id}: {str(e)}")
        db = SessionLocal()
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = "failed"
            db.commit()
        db.close()

# API Routes
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db.query(User).filter(User.phone == user.phone).first():
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Create new user
    hashed_password = hash_password(user.password)
    db_user = User(
        email=user.email,
        phone=user.phone,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse(
        id=db_user.id,
        email=db_user.email,
        phone=db_user.phone,
        full_name=db_user.full_name,
        is_active=db_user.is_active,
        created_at=db_user.created_at
    )

@app.post("/auth/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not db_user.is_active:
        raise HTTPException(status_code=400, detail="Account is deactivated")
    
    # Create access token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=db_user.id,
            email=db_user.email,
            phone=db_user.phone,
            full_name=db_user.full_name,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        phone=current_user.phone,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )

@app.post("/videos/upload", response_model=VideoResponse)
async def upload_video(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Validate file type
    if not file.content_type.startswith('video/'):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    input_path = f"uploads/{unique_filename}"
    output_path = f"processed/{unique_filename}"
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Create database record
    db_video = Video(
        user_id=current_user.id,
        original_filename=file.filename,
        processed_filename=unique_filename,
        status="processing"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    
    # Start background processing
    executor.submit(process_video_sync, db_video.id, input_path, output_path)
    
    return VideoResponse(
        id=db_video.id,
        original_filename=db_video.original_filename,
        processed_filename=db_video.processed_filename,
        status=db_video.status,
        created_at=db_video.created_at,
        processing_time=db_video.processing_time
    )

@app.get("/videos", response_model=List[VideoResponse])
async def get_user_videos(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    videos = db.query(Video).filter(Video.user_id == current_user.id).order_by(Video.created_at.desc()).all()
    return [
        VideoResponse(
            id=video.id,
            original_filename=video.original_filename,
            processed_filename=video.processed_filename,
            status=video.status,
            created_at=video.created_at,
            processing_time=video.processing_time
        ) for video in videos
    ]

@app.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    video = db.query(Video).filter(Video.id == video_id, Video.user_id == current_user.id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return VideoResponse(
        id=video.id,
        original_filename=video.original_filename,
        processed_filename=video.processed_filename,
        status=video.status,
        created_at=video.created_at,
        processing_time=video.processing_time
    )

@app.get("/")
async def root():
    return {"message": "Sports Video Analysis API", "status": "running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
