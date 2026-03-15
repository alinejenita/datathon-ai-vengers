from fastapi import APIRouter, Depends
from backend.auth.jwt_handler import get_current_user
from backend.models import User

router = APIRouter()

@router.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "seller_name": current_user.seller_name
    }