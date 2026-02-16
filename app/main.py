from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.user_database import engine, Base, SessionLocal
from app.models.user_models import User
from app.routes.user_routes import router as user_router
from app.models.user_location_model import UserLocation


app = FastAPI(title="User Management API")




origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "API is working"}


@app.on_event("startup")
def add_sample_user():
    db = SessionLocal()
    try:
        exists = db.query(User).filter(User.email == "john@gmail.com").first()
        if not exists:
            sample_user = User(
                first_name="John",
                last_name="Doe",
                email="john@gmail.com",
                phone_number="9876543210",
                is_active=True
            )
            db.add(sample_user)
            db.commit()
    finally:
        db.close()


app.include_router(user_router)

# Backend structure cleanup - PR demo
