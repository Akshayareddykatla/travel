from flask_sqlalchemy import SQLAlchemy
from flask import Flask

app = Flask(__name__)

# Configure SQLite DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    full_name = db.Column(db.String(120))
    bio = db.Column(db.Text)
    interests = db.Column(db.String(255))
    phone = db.Column(db.String(20))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Database and tables created successfully!")
