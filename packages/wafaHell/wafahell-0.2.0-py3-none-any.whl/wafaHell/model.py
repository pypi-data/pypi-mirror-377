from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

Base = declarative_base()

class Blocked(Base):
    __tablename__ = "blocks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    ip = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    blocked_at = Column(String, nullable=False, default=lambda: datetime.now().strftime("%H:%M:%S"))

    def __repr__(self):
        return f"<Blocked(ip='{self.ip}', user_agent='{self.user_agent}', blocked_at='{self.blocked_at}')>"

def get_session(db_url="sqlite:///wafaHell.db"):
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)
    return Session
