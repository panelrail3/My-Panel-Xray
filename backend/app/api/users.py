import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserResponse
from ..security import require_admin

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    return db.query(User).order_by(User.id.desc()).all()

@router.post("", response_model=UserResponse)
def create_user(data: UserCreate, db: Session = Depends(get_db), _=Depends(require_admin)):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(status_code=409, detail="Username already exists")
    u = User(username=data.username, uuid=str(uuid.uuid4()), traffic_limit=data.traffic_limit, expire_at=data.expire_at)
    db.add(u); db.commit(); db.refresh(u)
    return u
