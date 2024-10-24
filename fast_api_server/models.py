from sqlalchemy import JSON, Column, Enum, Integer, String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, nullable=True)  # Nullable because it's set after OAuth
    picture = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Single relationship that includes all games the user is in
    games = relationship("Game", 
                        primaryjoin="or_(User.id==Game.player1_id, User.id==Game.player2_id)",
                        lazy="dynamic")
    
    # Single relationship that includes all lobby tables the user is in
    lobby_tables = relationship("LobbyTable",
                              primaryjoin="or_(User.id==LobbyTable.player1_id, User.id==LobbyTable.player2_id)",
                              lazy="dynamic")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    
    # Foreign keys to users
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    
    # Keep these as temporary fields for backward compatibility during migration
    player1_token = Column(String, nullable=True)
    player2_token = Column(String, nullable=True)
    
    game_state = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Simple relationships to users
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])

class LobbyTable(Base):
    __tablename__ = "lobby_tables"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum("Waiting", "Full", name="lobby_status"))
    
    # Foreign keys to users
    player1_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    player2_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Keep these as temporary fields for backward compatibility during migration
    player1_token = Column(String, nullable=True)
    player2_token = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Simple relationships to users
    player1 = relationship("User", foreign_keys=[player1_id])
    player2 = relationship("User", foreign_keys=[player2_id])