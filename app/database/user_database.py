from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://postgres:%40Badusha7@localhost:5432/user_db"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# try:
#     with engine.connect() as connection:
#         print("Database connected successfully ✅")
# except Exception as e:
#     print("Connection failed ❌", e)
