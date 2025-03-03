import unittest
from models.user import User
from models import storage
from models.stock import Stock
from models.area import Area
from models.cart import Cart

class test_models(unittest.TestCase):
    def test_all_models(self):
        user = User(name='Shadya Obuya', password='opoooo', email='ShadyaObuya@gmail.com', location='Nairobi')
        stock1= Stock(product='Chips', value=100, description='A plate of chips', category='Foods')
        storage.new(stock1)
        storage.save()
        users_id = user.id
        al = storage.all(Stock).values()
        self.assertIn(stock1, al)
        product2 = Cart(item=stock1.product, price=stock1.value, description=stock1.description, category=stock1.category, user_id='27d0a2ea-45fb-4889-89a1-5526f074946c')
        storage.new(product2)
        storage.save()
        b = storage.all(Cart).values()
        self.assertIn(product2, b)
        