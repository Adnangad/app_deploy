from flask import Flask, request, jsonify, redirect, render_template, url_for, session, send_from_directory, json
from models.user import User
from models import storage
from models.area import Area
from models.stock import Stock
from flask_cors import CORS
from models.cart import Cart
from uuid import uuid4
import os
import requests
from collections import defaultdict
from math import ceil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.exc import SQLAlchemyError
from instances import initialize_db

app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
CORS(app)
cache_id = uuid4()
"""SMTP_SERVER = os.getenv('SERVER')
SMTP_PORT = 587
SMTP_USERNAME = os.getenv('USERNAME')
SMTP_PASSWORD = os.getenv('SMTP-PASSWORD')
FROM_EMAIL = os.getenv('EMAIL')
CREATOR_EMAIL = os.getenv('EMAIL')"""

initialize_db()

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def home():
    return "Successfully running"

@app.route("/location", methods=['POST'])
def check_Area():
    """Checks if the entered location  is within the database"""
    try:
        area = storage.all(Area).values()
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Please enter a valid location'}), 400
        loc = data.get('area') 
        for a in area:
            if loc == a.name:
                return jsonify({'message': 'We do deliver in that location'}), 200
        return jsonify({'message': 'Sorry but we are not yet available in that location'}), 400
    except SQLAlchemyError as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/moreinfo', methods=["GET"])
def get_inf():
    """Renders the template inf.html"""
    return render_template("inf.html")

@app.route("/login", methods=["POST"])
def sign_in():
    """Checks if the user exists in the databse"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request must be JSON.'}), 400
        mail = data['email']
        password = data['password']
        users = storage.all(User).values()
        for user in users:
            if user.email == mail:
                real_user = storage.get(User, user.id)
                if real_user.password == password:
                    session['user_id'] = real_user.id
                    return jsonify({'message': 'Login successful', 'user': real_user.to_dict()}), 200
        return jsonify({'message': 'Invalid email or password.'}), 401
    except Exception as e:
        print(e)
        storage.rollback()
        return jsonify({'message': str(e)}), 500

@app.route("/sign_up", methods=['POST'])
def sign_up():
    """Adds a users to the database"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request must be JSON.'}), 400
        mail = data['email']
        users = storage.all(User).values()
        for user in users:
            if user.email == mail:
                return jsonify({'message': 'Email Adress already exists.'}), 400
        new_user = User(**data)
        storage.new(new_user)
        storage.save()
        return jsonify({'message': 'You have been successfully added to the database, you can now login', 'user': new_user.to_dict()}), 200
    except SQLAlchemyError as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500

@app.route("/add_to_cart", methods=['POST'])
def add_to_cart():
    """Adds an item to the cart"""   
    try:
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request must be JSON.'}), 400
        if isinstance(data['user'], dict):
            userz = data['user']
            user = storage.get(User, userz['id'])
        else:
            userz = json.loads(data['user'])
            user = storage.get(User, userz['id'])
        stock = data['stock']
        
        if not user:
            return jsonify({'message': 'User not found. Please login again.'}), 401    
            
        cart_item = Cart(user_id=user.id, item=stock['product'], price=stock['value'], image=stock['image'])
        storage.new(cart_item)
        storage.save()
        storage.reload()
        number_of_items = sum(1 for cart in storage.all(Cart).values() if cart.user_id == user.id and cart.item == cart_item.item)
        return jsonify({'message': 'Item added to cart successfully', 'number_of_items': number_of_items, 'cart_item': cart_item.id}), 200
    except Exception as e:
        storage.rollback()
        print(e)
        return jsonify({'message': str(e)}), 500

@app.route('/remove_item', methods=['DELETE'])
def remove_from_cart():
    """Removes an item from the cart"""
    try:
        print("here it starts")
        data = request.get_json()
        print(data)
        if not data:
            return jsonify({'message': 'Request must be JSON.'}), 400
        if isinstance(data['user'], dict):
            userz = data['user']
            user = storage.get(User, userz['id'])
        else:
            userz = json.loads(data['user'])
            user = storage.get(User, userz['id'])
        if not user:
            return jsonify({'message': 'Please login.'}), 401
        cart_item = storage.get(Cart, data['cart_id'])
        if cart_item is None:
            return jsonify({'message': 'Not found'}), 400
        storage.delete(cart_item)
        storage.save()
        storage.reload()
        print("Its deleeted")
        number_of_items = sum(1 for cart in storage.all(Cart).values() if cart.user_id == user.id and cart.item == cart_item.item)
        return jsonify({'message': 'Item removed from cart successfully', 'number_of_items': number_of_items}), 200
    except Exception as e:
        storage.rollback()
        print(e)
        return jsonify({'message': str(e)}), 500


@app.route("/getmenu", methods=['GET'], strict_slashes=False)
def get_menu():
    """Renders the menu page with optional category filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        category = request.args.get('category', None)

        stocks = list(storage.all(Stock).values())

        if category and category.lower() != "all_items":
            stocks = [stock for stock in stocks if stock.category.lower() == category.lower()]

        stocks.sort(key=lambda x: x.product)

        total_stocks = len(stocks)
        total_pages = (total_stocks + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        paginated_stocks = stocks[start:end]

        stocks_dict = [stock.to_dict() for stock in paginated_stocks]

        return jsonify({'stocks': stocks_dict, 'page': page, 'total_pages': total_pages}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/cart/<user_id>", methods=["GET"])
def show_cart(user_id):
    """Returns the cart page with a list of items in the cart"""
    try:
        user = storage.get(User, user_id)
        if not user:
            return jsonify({'message': 'Please login.'}), 401
        
        carts = sorted(list(storage.all(Cart).values()), key=lambda x: x.item)
        grouped_carts = defaultdict(lambda: {'count': 0, 'details': {}})
        total_price = 0
        print("here")
        for cart in carts:
            if cart.user_id == user.id:
                item_name = cart.item
                grouped_carts[item_name]['count'] += 1
                grouped_carts[item_name]['details'] = {
                    'id': cart.id,
                    'user_id': cart.user_id,
                    'item': cart.item,
                    'price': float(cart.price),  # Ensure it's a serializable number
                    'image': cart.image
                }
                total_price += float(cart.price)
        
        return jsonify({'user': {'id': user.id, 'name': user.name}, 'grouped_carts': dict(grouped_carts), 'total_price': total_price}), 200

    except Exception as e:
        storage.rollback()
        print(e)
        return jsonify({'message': str(e)}), 500

@app.route('/user/', methods=['GET'])
def user_info():
    """Navigates to the user account page"""
    if 'user_id' not in session:
        return jsonify({'message': 'User does not exist'}), 400
    try:
        user_id = session['user_id']
        user = storage.get(User, user_id)
        stocks = sorted(list(storage.all(Stock).values()), key=lambda x: x.product)
        return render_template('user.html', user=user, stocks=stocks)
    except SQLAlchemyError as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500


@app.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Deletes a user from the database"""
    try:
        user = storage.get(User, user_id)
        storage.delete(user)
        del(session['user_id'])
        storage.save()
        storage.reload()
        return jsonify({"message":"Your account has been deleted permanently"}), 200
    except Exception as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500

@app.route('/update_user', methods=['PUT'])
def update_user():
    """Updates the users details"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Data must be in json format"}), 400
        user_id = data['user_id']
        user = storage.get(User, user_id)
        if not user:
            return jsonify({"error": "User doesn't exist"}), 400
        for key, value in data.items():
            if key not in ['user_id', 'email']:
                setattr(user, key, value)
        user.save()
        return jsonify({"message": "You have successfully updated your details"}), 200
    except SQLAlchemyError as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500

"""def send_email(user_email, creator_email, order_details):
    message = MIMEMultipart()
    message['From'] = FROM_EMAIL
    message['To'] = ', '.join([user_email, creator_email])
    message['Subject'] = 'Order Details'
    
    # Create the plain text part of the message
    text = f'Order Details:\n{order_details}'
    message.attach(MIMEText(text, 'plain'))
    
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, [user_email, creator_email], message.as_string())
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")"""

"""@app.route('/payment', methods=['POST'])
def mobile_payment():
    if 'user_id' not in session:
        return jsonify({'message': 'Please login.'}), 401
    try:
        user_id = session['user_id']
        user = storage.get(User, user_id)
        if not user:
            return jsonify({'message': 'User not found.'}), 404

        carts = sorted(list(storage.all(Cart).values()), key=lambda x: x.item)
        order_details = {}
        for cart in carts:
            if cart.user_id == user.id:
                order_details[cart.item] = cart.price

        order_details_str = f"name:{user.name}\nuser_id:{user.id}\n" + "\n".join([f"{item}: ksh{price}" for item, price in order_details.items()])
        send_email(user.email, CREATOR_EMAIL, order_details_str)
        
        return render_template('success.html', user=user)
    except SQLAlchemyError as e:
        storage.rollback()
        return jsonify({'message': str(e)}), 500"""

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
