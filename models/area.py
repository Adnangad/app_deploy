from models.base_model import BaseModel, Base
from sqlalchemy import *
from sqlalchemy.orm import relationship

class Area(BaseModel, Base):
    """Creates a table areas"""
    __tablename__ = 'areas'
    name = Column(String(60), nullable=False)