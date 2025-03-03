from sqlalchemy import *
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User
from models.cart import Cart
from models.stock import Stock
from models.area import Area
import os

classes = {"User": User, "Cart": Cart, "Stock": Stock, "Area": Area}

class DBStorage:
    __engine = None
    __session = None
    
    def __init__(self):
        """creates engine and instanciates"""
        database_url = os.getenv('DATABASE_URL', 'mysql+mysqlconnector://temp:password@localhost/mydatabase')
        print(f"Using database URL: {database_url}")
        self.__engine = create_engine(database_url)
    
    def all(self, cls=None):
        """Lists all objects in db"""
        temp = {}
        for clas in classes:
            if cls is None or cls is classes[clas] or cls is clas:
                objs = self.__session.query(classes[clas]).all()
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    temp[key] = obj
        return temp
    
    def new(self, obj):
        """Adds a new object to database"""
        self.__session.add(obj)
    
    def save(self):
        """Saves changes to a db"""
        self.__session.commit()
    
    def delete(self, obj=None):
        """Deletes an obj from database"""
        if obj is not None:
            self.__session.delete(obj)
    
    def get(self, cls, id):
        """Retrieves a specific object from db based on cls and id"""
        try:
            return self.__session.query(cls).filter(cls.id == id).first()
        except Exception:
            return None
    
    def count(self, cls=None):
        """Counts the numb of instances of a class"""
        if cls is not None:
            count = self.__session.query(cls).count()
            return count
        else:
            num = 0
            rez = self.all()
            for _ in rez:
                num = num + 1
            return rez
    
    def reload(self):
        """Reloads the db"""
        Base.metadata.create_all(self.__engine)
        session_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(session_factory)
        self.__session = Session()
    
    def close(self):
        """call remove() method on the private session attribute"""
        self.__session.remove()
    
    def rollback(self):
        """Rolls back the current session"""
        self.__session.rollback()