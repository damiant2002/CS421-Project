from flask import Flask, render_template, url_for, flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, asc
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    current_user,
    logout_user,
    login_required,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_migrate import Migrate
from datetime import datetime
import email_validator
import random
import math

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"
migrate = Migrate(app, db)

class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    password = db.Column(db.String(60), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class PayRoll(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    payRate = db.Column(db.Float)
    payPeriod = db.Column(db.Float)
    YTD = db.Column(db.Float)
    hours = db.Column(db.Float)
    gross = db.Column(db.Float)
    tax = db.Column(db.Float)
    OT = db.Column(db.Float)
    net = db.Column(db.Float)

    def __init__(self, username, payRate, payPeriod, YTD, hours, gross, tax, OT, net):
        self.username = username
        self.payRate = payRate
        self.payPeriod = payPeriod
        self.YTD = YTD
        self.hours = hours
        self.gross = gross
        self.tax = tax
        self.OT = OT
        self.net = net

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                "That username is taken. Please choose a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError("That email is taken. Please choose a different one.")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class UpdateProfileForm(FlaskForm):
    username = StringField(
        "Username", validators=[DataRequired(), Length(min=2, max=20)]
    )
    email = StringField("Email", validators=[DataRequired(), Email()])
    address = StringField("Address", validators=[Length(max=200)])
    picture = StringField("Profile Picture URL")
    submit = SubmitField("Update")


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )

        if "register_as_admin" in request.form:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                is_admin=True,
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Admin account has been created!", "success")
            return redirect(url_for("thank_you"))
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                password=hashed_password,
                is_admin=False
            )
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account has been created!", "success")
            return redirect(url_for("thank_you"))

    return render_template("register.html", title="Register", form=form)


@app.route("/thank_you")
@login_required
def thank_you():
    return render_template("thanks.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login Unsuccessful. Please check email and password", "danger")
    return render_template("login.html", title="Login", form=form)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.address = form.address.data
        if form.picture.data:
            current_user.image_file = form.picture.data
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.address.data = current_user.address
        form.picture.data = current_user.image_file
    return render_template("profile.html", title="Profile", form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))

@app.route("/PayView")
def PayView():
    if (not current_user):
        return redirect(url_for("login"))
    
    if is_admin(current_user):
        pays = PayRoll.query.all()
        return render_template('PayView.html', pays=pays)
    
    else:    
        userName = current_user.username
        
        paySlip = PayRoll.query.filter(PayRoll.username == userName).first()
        if (not paySlip):
            rate = round(random.uniform(20, 35), 2)

            newEmployeePaySlip = PayRoll(userName, rate, 1.0, 0, 0, 0, 0, 0, 0)
            paySlip = newEmployeePaySlip

            db.session.add(newEmployeePaySlip)
            db.session.commit()
        
        else:
            paySlip = PayRoll.query.filter(PayRoll.username == userName).order_by(desc(PayRoll.payPeriod)).first()

    payRate = paySlip.payRate

    workedHours = round(random.uniform(40, 55), 2)
    overTimeHours = workedHours - 40

    OTpay = (payRate * 1.5 * overTimeHours)
    OTpay = round(OTpay, 2)

    grossPay = ((workedHours * payRate) + OTpay)
    grossPay = round(grossPay, 2)

    taxPay = grossPay * 0.15
    taxPay = round(taxPay, 2)

    netPay = grossPay - taxPay
    netPay = round(netPay, 2)

    YTDamount = paySlip.YTD + netPay
    YTDamount = round(YTDamount, 2)

    payPeriod = calcPayPeriod(paySlip.payPeriod)

    newPaySlip = PayRoll(userName, payRate, payPeriod, YTDamount, workedHours, grossPay, taxPay, OTpay, netPay)
    db.session.add(newPaySlip)
    db.session.commit()

    allPaySlips = PayRoll.query.filter(PayRoll.username == userName).all()

    return render_template("PayView.html", pays=allPaySlips)

@app.route("/users")
def users():
    if (not current_user):
        return redirect(url_for("login")) 
    users = User.query.all()
    return render_template('users.html', users=users)
    
    
def calcPayPeriod(period: float):
    period = period + 0.01
    period = round(period, 2)
    test = math.ceil(period)

    if (test-period <= 0.48):
        return test
    else:
        return period

@app.context_processor
def inject_functions():
    return dict(is_admin=is_admin)

def is_admin(user):
    if user.is_authenticated:
        return user.is_admin
    return False





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

