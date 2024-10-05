# models.py
from sqlalchemy import JSON, Column, Enum, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Game(Base):
    __tablename__ = "games"
    id = Column(Integer, primary_key=True, index=True)
    status = Column(String)
    player1_token = Column(String)
    player2_token = Column(String)
    game_state = Column(JSON)
   
    websocket1 = None
    websocket2 = None

class LobbyTable(Base):
    __tablename__ = "lobby_tables"
   
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    status = Column(Enum("Waiting", "Full", name="lobby_status"))
    player1_token = Column(String)
    player2_token = Column(String)

