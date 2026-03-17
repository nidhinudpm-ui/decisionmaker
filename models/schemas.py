from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Decision(db.Model):
    __tablename__ = 'decisions'
    id = db.Column(db.Integer, primary_key=True)
    goal = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    options = db.relationship('Option', backref='decision', lazy=True, cascade="all, delete-orphan")
    criteria = db.relationship('Criterion', backref='decision', lazy=True, cascade="all, delete-orphan")

class Option(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, primary_key=True)
    decision_id = db.Column(db.Integer, db.ForeignKey('decisions.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    pdf_path = db.Column(db.String(512), nullable=True)
    
    scores = db.relationship('CriterionScore', backref='option', lazy=True, cascade="all, delete-orphan")

class Criterion(db.Model):
    __tablename__ = 'criteria'
    id = db.Column(db.Integer, primary_key=True)
    decision_id = db.Column(db.Integer, db.ForeignKey('decisions.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.Float, nullable=False)  # 0 to 100
    type = db.Column(db.String(50), nullable=False)  # 'numeric' or 'qualitative'
    direction = db.Column(db.String(50), nullable=False)  # 'higher_better' or 'lower_better'

class CriterionScore(db.Model):
    __tablename__ = 'criterion_scores'
    id = db.Column(db.Integer, primary_key=True)
    option_id = db.Column(db.Integer, db.ForeignKey('options.id'), nullable=False)
    criterion_id = db.Column(db.Integer, db.ForeignKey('criteria.id'), nullable=False)
    raw_value = db.Column(db.Float, nullable=True)
    score = db.Column(db.Float, nullable=True)  # Normalized score 0-10
    evidence_text = db.Column(db.Text, nullable=True)
    evidence_page = db.Column(db.Integer, nullable=True)
