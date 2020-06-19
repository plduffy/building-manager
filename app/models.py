from app import db, login, app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
from time import time
import jwt

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    budget = db.Column(db.Float, index=True)
    transactions = db.relationship('ProjectTransaction', lazy='dynamic', backref='project')

    def __repr__(self):
        return '<Project {}'.format(self.name)

class Vendor(db.Model):
    __tablename__ = 'vendors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True, unique=True)
    phone_number = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True)
    transactions = db.relationship('ProjectTransaction', lazy='dynamic', backref='vendor')

    def __repr__(self):
        return '<Vendor {}>'.format(self.name)

class ProjectTransaction(db.Model):
    __tablename__ = 'project_transactions'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    date = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    amount = db.Column(db.Float)
    description = db.Column(db.String(256), index=True)

    def __repr__(self):
        return '<Project Transaction {}>'.format(self.id)

class Invoice(db.Model):
    __tablename__ = 'models'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, index=True)
    description = db.Column(db.String, index=True)
    invoice_date = db.Column(db.DateTime, index=True)
    paid_date = db.Column(db.DateTime, index=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
