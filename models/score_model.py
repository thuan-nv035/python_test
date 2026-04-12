from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    points = db.Column(db.Integer)
