# backend/main.py (Updated Complete Version)
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import timedelta

from models.base import get_db, engine, Base
from models.user import User
from models.profile import LinkedInProfile
from schemas.user import UserCreate, UserResponse, Token
from services.auth import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    verify_token
)

# Import API routers
from api.agents import router as agents_router
from api.profiles import router as profiles_router
from api.analytics import router as analytics_router

# Create database tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LinkedIntelligence API",
    description="AI-powered LinkedIn automation and intelligence platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - configure for production
origins = [
    "http://localhost:3000",  # React dev server
    "http://localhost:3001",  # Alternative dev port
    "https://yourdomain.com"  # Production domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    email = verify_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# Include API routers
app.include_router(agents_router)
app.include_router(profiles_router)
app.include_router(analytics_router)

# Health check endpoints
@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "linkedintelligence-api",
        "version": "1.0.0"
    }

@app.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)):
    try:
        # Test database connection
        result = db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Database connection failed: {str(e)}"
        )

# Authentication endpoints
@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        linkedin_profile_url=user.linkedin_profile_url
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login", response_model=Token)
async def login(user: UserCreate, db: Session = Depends(get_db)):
    """Authenticate user and return access token"""
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return {
        "detail": "Internal server error",
        "status_code": 500,
        "error_type": type(exc).__name__
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )