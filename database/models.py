# database/models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from settings import DB_NAME

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    city = Column(String)
    
    tickets = relationship("Ticket", back_populates="user")

class Ticket(Base):
    __tablename__ = 'tickets'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    ticket_type = Column(String)  # 'flight', 'flight_transfer', 'train', 'train_transfer'
    departure_date = Column(DateTime)
    route = Column(String)  # Для билетов без пересадки
    route_part1 = Column(String)  # Для билетов с пересадкой
    route_part2 = Column(String)  # Для билетов с пересадкой
    flight_number = Column(String)
    company = Column(String)
    has_baggage = Column(Boolean)
    price = Column(Float)
    created_at = Column(DateTime)
    
    user = relationship("User", back_populates="tickets")

# Инициализация БД
engine = create_engine(f'sqlite:///{DB_NAME}')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
