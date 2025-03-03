"""
This module adds items to the database for consumers to choose.
"""
from models.stock import Stock
from models import storage
from models.area import Area
import os

# List of stock items to add
stock_items = [
    Stock(product='Beef_stew', value=150, description='A plate of beef stew', image='images/beef_stew.jpg', category='Foods'),
    Stock(product='Biriani', value=250, description='A plate of biriani', image='images/biriani.jpg', category='Foods'),
    Stock(product='Chapati', value=70, description='2 rolls of chapatis', image='images/chapati.jpg', category='Foods'),
    Stock(product='Chicken', value=200, description='3 pieces of chicken', image='images/chicken.jpg', category='Foods'),
    Stock(product='Coffee', value=50, description='A cup of coffee', image='images/coffee.jpg', category='Beverages'),
    Stock(product='Chips', value=175, description='A plate of chips', image='images/chips.jpg', category='Foods'),
    Stock(product='Fish', value=100, description='1 fried fish', image='images/fish.jpg', category='Foods'),
    Stock(product='Githeri', value=75, description='A plate of githeri', image='images/githeri.jpg', category='Foods'),
    Stock(product='Hamburger', value=100, description='One burger', image='images/hamburger.jpg', category='Foods'),
    Stock(product='Lemon tea', value=50, description='A cup of lemon tea', image='images/lemon_tea.jpg', category='Beverages'),
    Stock(product='Mango Juice', value=75, description='A glass of mango juice', image='images/mango_juice.jpg', category='Drinks'),
    Stock(product='Nyama Choma', value=200, description='A plate of nyama choma', image='images/nyama.jpg', category='Foods'),
    Stock(product='Orange Juice', value=75, description='A glass of orange juice', image='images/orange_juice.jpg', category='Drinks'),
    Stock(product='Pilau', value=200, description='A plate of pilau', image='images/pilau.jpg', category='Foods'),
    Stock(product='Samosas', value=50, description='1 meat samosa', image='images/samosa.jpg', category='Foods'),
    Stock(product='Sausages', value=60, description='2 sausages', image='images/sausage.jpg', category='Foods'),
    Stock(product='Tea', value=50, description='A cup of tea', image='images/tea.jpg', category='Beverages'),
    Stock(product='Ugali', value=40, description='A plate of plain ugali', image='images/ugali.jpg', category='Foods'),
    Stock(product='Water', value=65, description='A bottle of water', image='images/water.jpg', category='Drinks'),
]

# Fetch existing stock from the database
existing_stocks = {stock.product for stock in storage.all(Stock).values()}

# Add only new items to the database
for stock in stock_items:
    if stock.product not in existing_stocks:
        storage.new(stock)
        existing_stocks.add(stock.product)  # Update seen products

# Save changes to the database
storage.save()
