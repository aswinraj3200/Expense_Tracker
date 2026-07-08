from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    product_name = db.Column(db.String(100), nullable=False)

    category = db.Column(db.String(50), nullable=False)

    amount = db.Column(db.Float, nullable=False)

    notes = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)