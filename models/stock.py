from models.base_model import Base, BaseModel
from sqlalchemy import *
from sqlalchemy.orm import relationship

class Stock(BaseModel, Base):
    """Creates a class"""
    __tablename__ = 'stocks'
    product = Column(String(90), nullable=False)
    value = Column(VARCHAR(90), nullable=False)
    description = Column(String(300))
    image = Column(String(200))
    category = Column(String(80), nullable=False)