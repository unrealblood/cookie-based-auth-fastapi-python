from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
from os import getenv

load_dotenv()

db_engine = create_engine(getenv("DATABASE_URL"), connect_args={"check_same_thread":False})

local_session = sessionmaker(bind=db_engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement="auto")
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

Base.metadata.create_all(bind=db_engine)

def get_db():
    db = local_session()

    try:
        yield db
    except Exception as e:
        print(e)
    finally:
        db.close()