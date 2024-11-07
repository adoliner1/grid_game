from sqlalchemy import JSON, Column, Enum, Integer, String, DateTime
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
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    last_login = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    player1_id = Column(String)  # Will store google_id or guest UUID
    player2_id = Column(String)  # Will store google_id or guest UUID
    game_state = Column(JSON)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class LobbyTable(Base):
    __tablename__ = "lobby_tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum("Waiting", "Full", name="lobby_status"))
    player1_id = Column(String, nullable=True)  # Will store google_id or guest UUID
    player2_id = Column(String, nullable=True)  # Will store google_id or guest UUID
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))