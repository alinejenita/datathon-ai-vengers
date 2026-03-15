from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.models import UserCreate, UserLogin, UserResponse, SuccessResponse
from backend.db.postgres import get_db
from backend.auth.password_utils import hash_password, verify_password
from backend.auth.jwt_handler import create_access_token
from backend.models import User  # We'll create this SQLAlchemy model in Step 6

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=SuccessResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(
        email=user.email,
        seller_name=user.seller_name,
        password_hash=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"success": True, "message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"user_id": db_user.id})
    return {"access_token": token, "token_type": "bearer"}