
from typing import Optional
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session

from app.models.user_models import User
from app.models.user_location_model import UserLocation
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.ip_utils import get_client_ip
from app.utils.location_service import fetch_location



def _save_user_location(db: Session, user_id: int, request: Request) -> None:
    """
    Fetches client IP -> location -> stores in user_locations table.
    This should NOT break the main API even if location fails.
    """
    try:
        ip = get_client_ip(request)
        if not ip:
            return

        loc_data = fetch_location(ip)
        if not isinstance(loc_data, dict):
            loc_data = {}

        location = UserLocation(
            user_id=user_id,
            ip_address=ip,
            country=loc_data.get("country"),
            state=loc_data.get("regionName"),
            latitude=loc_data.get("lat"),
            longitude=loc_data.get("lon"),
        )

        db.add(location)
        db.commit()

    except Exception:
        db.rollback()
        
        return



def get_users_service(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    is_active: Optional[bool] = True,
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



def get_user_by_id_service(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user



def create_user_service(db: Session, payload: UserCreate, request: Request):
    # Email uniqueness check
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")

    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)


    _save_user_location(db, user.id, request)

    return user



def update_user_service(db: Session, user_id: int, payload: UserUpdate, request: Request):
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

    # Update fields
    for key, value in data.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)

    _save_user_location(db, user.id, request)

    return user



def delete_user_service(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()
    return None
