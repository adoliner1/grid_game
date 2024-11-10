from sqlalchemy import JSON, Column, Enum, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
   
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, nullable=True)
    picture = Column(String, nullable=True)
    elo_rating = Column(Integer, default=1200)
    wins = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    player1_id = Column(String)  
    player2_id = Column(String)  
    game_state = Column(JSON)
    is_ranked = Column(Boolean, default=False)
    winner_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class LobbyTable(Base):
    __tablename__ = "lobby_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum("Waiting", "Full", name="lobby_status"))
    player1_id = Column(String, nullable=True)  
    player2_id = Column(String, nullable=True)  
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))