from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class EquipmentRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_number = db.Column(db.String(10), unique=True, nullable=False)
    request_date = db.Column(db.String(10), nullable=False)
    equipment_name = db.Column(db.String(255), nullable=False)
    fault_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    client_name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    assigned_to = db.Column(db.String(255), nullable=True)  # Изменим на nullable=True
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    created_by = db.Column(db.String(50))
    comments = db.relationship('Comment', backref='request', lazy=True)
    
    

    def __init__(self, request_number, request_date, equipment_name, fault_type, description, client_name, status, assigned_to=None, start_date=None, end_date=None, created_by=None ):
        self.request_number = request_number
        self.request_date = request_date
        self.equipment_name = equipment_name
        self.fault_type = fault_type
        self.description = description
        self.client_name = client_name
        self.status = status
        self.assigned_to = assigned_to
        self.start_date = start_date
        self.end_date = end_date
        self.created_by = created_by
        

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    request_id = db.Column(db.Integer, db.ForeignKey('equipment_request.id'), nullable=False)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    intro = db.Column(db.String(100), nullable=False)
    rev_text = db.Column(db.String(255), nullable=False)
    
    
    def __repr__(self):
        return '<Review %r>' % self.id
    
class Masters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    level = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(300),nullable=False)
