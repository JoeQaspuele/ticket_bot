# database/db_operations.py
from sqlalchemy.exc import SQLAlchemyError
from database.models import Session, User, Ticket
from datetime import datetime

class DBOperations:
    @staticmethod
    def get_session():
        return Session()
    
    @staticmethod
    def add_user(session, telegram_id, first_name, last_name, middle_name, city):
        try:
            user = User(
                telegram_id=telegram_id,
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                city=city
            )
            session.add(user)
            session.commit()
            return user
        except SQLAlchemyError as e:
            session.rollback()
            raise e
    
    @staticmethod
    def get_user_by_telegram_id(session, telegram_id):
        return session.query(User).filter_by(telegram_id=telegram_id).first()
    
    @staticmethod
    def add_ticket(session, user_id, ticket_data):
        try:
            ticket = Ticket(
                user_id=user_id,
                **ticket_data,
                created_at=datetime.now()
            )
            session.add(ticket)
            session.commit()
            return ticket
        except SQLAlchemyError as e:
            session.rollback()
            raise e
    
    @staticmethod
    def get_user_tickets(session, user_id, limit=None):
        query = session.query(Ticket).filter_by(user_id=user_id).order_by(Ticket.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @staticmethod
    def get_all_tickets(session):
        return session.query(Ticket).order_by(Ticket.created_at.desc()).all()
