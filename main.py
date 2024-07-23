import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "data.sqlite"
)
app.config["SQLALCHEMY_TRAC_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# database tables
class User(db.Model):
    __tablename__ = "users"

    username = db.Column(db.String(120), primary_key=True)
    first = db.Column(db.String(80))
    last = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(120))
    role = db.Column(db.String(15))

    def __init__(self, username, first, last, email, password, role):
        self.username = username
        self.first = first
        self.last = last
        self.email = email
        self.password = password
        self.role = role


class Pay(db.Model):
    __tablename__ = "payroll"

    username = db.Column(db.String(120), primary_key=True)
    gross = db.Column(db, float)
    net = db.Column(db, float)
    tax = db.Column(db, float)
    overtime = db.Column(db, float)
    hours = db.Column(db, float)

    def __init__(self, username, gross, net, tax, overtime, hours):
        self.username = username
        self.gross = gross
        self.net = net
        self.tax = tax
        self.overtime = overtime
        self.hours = hours


# TODO: continue making appropriate tables


@app.route("/")
def index():
    return render_template("html login page here")


# TODO: @app.route() for other HTML pages

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
