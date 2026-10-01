import warnings
import secrets
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import jwt, JWTError
from loguru import logger
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from app.core.database import get_db
from app.models.user import User
from app.config import settings
from app.core.rate_limit import limiter

# Suppress passlib's bcrypt __about__ warning (bcrypt 4.x compatibility)
warnings.filterwarnings("ignore", ".*error reading bcrypt version.*")


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 1 week

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class GoogleToken(BaseModel):
    token: str

def verify_password(plain_password, hashed_password):
    # bcrypt max is 72 bytes — truncate consistently
    truncated = plain_password[:72] if isinstance(plain_password, str) else plain_password
    return pwd_context.verify(truncated, hashed_password)

def get_password_hash(password):
    # bcrypt max is 72 bytes — truncate consistently
    truncated = password[:72] if isinstance(password, str) else password
    return pwd_context.hash(truncated)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=ALGORITHM)
    return encoded_jwt

# Dependency to get current user from token
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    user = db.query(User).filter(User.username == username).first()
    return user

@router.post("/register", response_model=Token)
@limiter.limit("10/minute")
def register(request: Request, response: Response, user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Register attempt | username={user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        logger.warning(f"Register failed – username taken | username={user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f"User registered | username={user.username}")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}

@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
def login(request: Request, response: Response, user: UserLogin, db: Session = Depends(get_db)):
    logger.info(f"Login attempt | username={user.username}")
    db_user = db.query(User).filter(User.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        logger.warning(f"Login failed | username={user.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info(f"Login success | username={user.username}")
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}

@router.post("/google", response_model=Token)
@limiter.limit("10/minute")
def google_auth(request: Request, response: Response, google_token: GoogleToken, db: Session = Depends(get_db)):
    logger.info("Google OAuth attempt")
    try:
        idinfo = id_token.verify_oauth2_token(
            google_token.token, 
            google_requests.Request(), 
            "712901080417-f95lujh62r0366ihvquksl1ffjp0amvf.apps.googleusercontent.com"
        )
        email = idinfo.get('email')
        if not email:
            raise ValueError("Email not found in Google token")
        username = email
    except ValueError as e:
        logger.warning(f"Google token invalid: {e}")
        raise HTTPException(status_code=400, detail="Invalid Google token")

    db_user = db.query(User).filter(User.username == username).first()
    if not db_user:
        # Create user with random secure password
        random_password = secrets.token_urlsafe(32)
        hashed_password = get_password_hash(random_password)
        db_user = User(username=username, password_hash=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
    access_token = create_access_token(data={"sub": db_user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": db_user.username}
