from models.base_model import Base, BaseModel
from sqlalchemy import *
from sqlalchemy.orm import relationship

class Cart(BaseModel, Base):
    """Creates a class"""
    __tablename__ = 'carts'
    item = Column(String(70), nullable=False)
    price = Column(VARCHAR(70), nullable=False)
    image = Column(String(200))
    user_id = Column(String(60), ForeignKey("users.id"), nullable=False)
    user = relationship('User', back_populates='carts')