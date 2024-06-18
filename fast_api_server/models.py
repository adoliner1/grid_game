# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = "postgresql://myuser:mypassword@localhost/mydatabase"

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, index=True)
    players = relationship("Player", back_populates="game")

class LobbyTable(Base):
    __tablename__ = "lobby_tables"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(String, index=True)
    players = relationship("Player", back_populates="lobby_table")

class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    game_id = Column(Integer, ForeignKey('games.id'), nullable=True)
    lobby_table_id = Column(Integer, ForeignKey('lobby_tables.id'), nullable=True)
    game = relationship("Game", back_populates="players")
    lobby_table = relationship("LobbyTable", back_populates="players")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

