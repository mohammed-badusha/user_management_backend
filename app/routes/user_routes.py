# app/routes/user_routes.py
from fastapi import APIRouter, Depends, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from app.database.user_database import get_db
from app.schemas.user_schemas import UserCreate, UserUpdate, UserResponse, PaginatedUsers

from app.services.user_service import (
    get_users_service,
    get_user_by_id_service,
    create_user_service,
    update_user_service,
    delete_user_service,
)

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", response_model=PaginatedUsers)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = Query(True),
    db: Session = Depends(get_db),
):
    return get_users_service(db=db, page=page, page_size=page_size, is_active=is_active)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id_service(db=db, user_id=user_id)


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    return create_user_service(db=db, payload=payload, request=request)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, payload: UserUpdate, request: Request, db: Session = Depends(get_db)):
    return update_user_service(db=db, user_id=user_id, payload=payload, request=request)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    return delete_user_service(db=db, user_id=user_id)
