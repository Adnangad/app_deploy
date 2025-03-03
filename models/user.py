from models.base_model import Base, BaseModel
from sqlalchemy import *
from sqlalchemy.orm import relationship

class User(BaseModel, Base):
    """Creates a class"""
    __tablename__ = 'users'
    name = Column(String(60), nullable=False)
    email = Column(VARCHAR(60), nullable=False)
    password = Column(VARCHAR(60), nullable=False)
    location = Column(VARCHAR(100), nullable=False)
    carts = relationship('Cart', back_populates='user', cascade="all, delete-orphan")