from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database.user_database import get_db
from app.models.user_models import User
from app.models.user_location_model import UserLocation
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, PaginatedUsers
from app.utils.ip_utils import get_client_ip
from app.utils.location_service import fetch_location

router = APIRouter(prefix="/api/v1/users", tags=["Users"])



@router.get("", response_model=PaginatedUsers)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = Query(True),  
    db: Session = Depends(get_db),
):
    query = db.query(User)

 
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total_count = query.count()

    users = (
        query.order_by(User.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "data": users,
    }



@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
   
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)

    ip = get_client_ip(request)
    loc_data = fetch_location(ip) if ip else {}

    if not isinstance(loc_data, dict):
        loc_data = {}

    location = UserLocation(
        user_id=user.id,
        ip_address=ip,
        country=loc_data.get("country"),
        state=loc_data.get("regionName"),
        latitude=loc_data.get("lat"),
        longitude=loc_data.get("lon"),
    )

    db.add(location)
    db.commit()

    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_unset=True)

  
    if "email" in data:
        existing = (
            db.query(User)
            .filter(User.email == data["email"], User.id != user_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Email already exists")


    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    ip = get_client_ip(request)
    loc_data = fetch_location(ip) if ip else {}

    if not isinstance(loc_data, dict):
        loc_data = {}

    location = UserLocation(
        user_id=user.id,
        ip_address=ip,
        country=loc_data.get("country"),
        state=loc_data.get("regionName"),
        latitude=loc_data.get("lat"),
        longitude=loc_data.get("lon"),
    )

    db.add(location)
    db.commit()

    return user



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return None  
