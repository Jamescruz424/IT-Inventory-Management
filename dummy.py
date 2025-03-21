import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize Flask App
app = Flask(__name__)

# Database Configuration (Render PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://happy_wrtr_user:IceMx6wGQFffEPMzKlc3vDhKMSxeVYfe@dpg-cved66btq21c73ed2t10-a.oregon-postgres.render.com/happy_wrtr'
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ User Model
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    # Relationships
    payments = db.relationship('Payment', backref='user', cascade="all, delete")
    placed_orders = db.relationship('PlacedOrders', backref='user', cascade="all, delete")
    cart_items = db.relationship('Cart', backref='user', cascade="all, delete")

# ✅ Payment Model
class Payment(db.Model):
    __tablename__ = 'payment'
    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    order_id = db.Column(db.Integer, nullable=True)  # Optional link to PlacedOrders; null until order is confirmed
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    payment_status = db.Column(db.String(20), default='Pending', nullable=False)
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# ✅ PlacedOrders Model
class PlacedOrders(db.Model):
    __tablename__ = 'placed_orders'
    order_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.item_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    item = db.relationship('MenuItem', backref='order_entries')

# ✅ MenuItem Model
class MenuItem(db.Model):
    __tablename__ = 'menu_item'
    item_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    group_type = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(255))

# ✅ Cart Model
class Cart(db.Model):
    __tablename__ = 'cart'
    cart_id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('menu_item.item_id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    added_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    item = db.relationship('MenuItem', backref='cart_entries')

    # Unique constraint to prevent duplicate items in a user's cart
    __table_args__ = (db.UniqueConstraint('id', 'item_id', name='unique_user_item'),)

# ✅ Initialize Database on First Run
with app.app_context():
    db.create_all()
    logger.info('✅ Database tables created successfully!')

# ✅ Run Flask Application
if __name__ == '__main__':
    logger.info('🚀 Starting Flask application...')
    app.run(debug=True)
