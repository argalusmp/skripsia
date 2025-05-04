from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, get_current_admin
from app.database import get_db
from app.users.models import User, UserResponse, UserProfileUpdate
from app.auth.utils import get_password_hash

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if profile_update.email:
        # Check if email is already taken
        existing_user = db.query(User).filter(User.email == profile_update.email).first()
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        current_user.email = profile_update.email
    
    if profile_update.password:
        current_user.password_hash = get_password_hash(profile_update.password)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/", response_model=list[UserResponse])
async def get_all_users(
    skip: int = 0, 
    limit: int = 100,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    users = db.query(User).offset(skip).limit(limit).all()
    return users