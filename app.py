from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
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
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TimeField, SelectField
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
    schedules = db.relationship('Schedule', backref='user', lazy=True)

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

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    shift_start = db.Column(db.Time, nullable=False)
    shift_end = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f"Schedule('{self.date}', '{self.shift_start}', '{self.shift_end}')"  

class ScheduleForm(FlaskForm):
    user_id = SelectField('Employee', coerce=int, validators=[DataRequired()])
    date = DateField('Date', validators=[DataRequired()])
    shift_start = TimeField('Shift Start', validators=[DataRequired()])
    shift_end = TimeField('Shift End', validators=[DataRequired()])
    submit = SubmitField('Add Shift')

@app.route("/admin/schedules")
@login_required
def schedules():
    if not current_user.is_admin:
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for("home"))
    
    all_schedules = db.session.query(Schedule, User).join(User).all()
    return render_template("schedules.html", all_schedules=all_schedules)

@app.route("/admin/addShift", methods=["GET", "POST"])
@login_required
def addShift():
    if not current_user.is_admin:
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for("home"))
    
    form = ScheduleForm()
    form.user_id.choices = [(user.id, user.username) for user in User.query.order_by(User.username).all()]
    if form.validate_on_submit():
        new_shift = Schedule(
            user_id=form.user_id.data,
            date=form.date.data,
            shift_start=form.shift_start.data,
            shift_end=form.shift_end.data
        )
        db.session.add(new_shift)
        db.session.commit()
        flash("Shift added successfully!", "success")
        return redirect(url_for("schedules"))
    return render_template("addShift.html", form=form)

@app.route("/admin/delete_shift/<int:schedule_id>")
@login_required
def delete_shift(schedule_id):
    if not current_user.is_admin:
        flash("You do not have permission to view this page.", "danger")
        return redirect(url_for("home"))
    
    shift = Schedule.query.get_or_404(schedule_id)
    db.session.delete(shift)
    db.session.commit()
    flash("Shift deleted successfully!", "success")
    return redirect(url_for("schedules"))


@app.route("/schedule")
@login_required
def schedule():
    schedules = Schedule.query.filter_by(user_id=current_user.id).all()
    return render_template("schedule.html", schedules=schedules)

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
        
        paySlip = PayRoll.query.filter(PayRoll.username == userName).order_by(desc(PayRoll.payPeriod)).first()
        if (not paySlip):
            rate = round(random.uniform(20, 35), 2)

            paySlip = PayRoll(userName, rate, 1.0, 0, 0, 0, 0, 0, 0)

            db.session.add(paySlip)
            db.session.commit()

    payRate = paySlip.payRate

    payPeriod, quarter, payPeriodRange= calcPayPeriod(paySlip.payPeriod)

    workedHours = round(random.uniform(40, 55) * 2, 2)
    overTimeHours = workedHours - 40

    OTpay = (payRate * 1.5 * overTimeHours)
    OTpay = round(OTpay, 2)
    grossPay = ((workedHours * payRate) + OTpay)
    grossPay = round(grossPay, 2)
    taxPay = grossPay * 0.15
    taxPay = round(taxPay, 2)
    netPay = grossPay - taxPay
    netPay = round(netPay, 2)

    YTDamount = 0
    if (payPeriod == payPeriodRange):
        YTDamount = grossPay
        payRate += 0.25
    else:
        YTDamount = paySlip.YTD + grossPay

    newPaySlip = PayRoll(userName, payRate, payPeriod, YTDamount, workedHours, grossPay, taxPay, OTpay, netPay)
    db.session.add(newPaySlip)
    db.session.commit()

    allPaySlips = PayRoll.query.filter(PayRoll.username == userName).all()
    ATamount = sum(payslip.gross for payslip in allPaySlips)

    yearsPaySlips = PayRoll.query.filter(PayRoll.username == userName, PayRoll.payPeriod >= payPeriodRange, PayRoll.payPeriod < payPeriodRange+1).order_by(desc(PayRoll.payPeriod)).all()
    
    netAmount = 0
    OTamount = 0
    for paySlip in yearsPaySlips:
        netAmount += paySlip.net
        OTamount += paySlip.OT

    sickTime = workedHours*0.09
    vacationTime = workedHours*0.1

    return render_template("PayView.html", pays=yearsPaySlips, quarter=quarter, ATamount=ATamount, sickTime=sickTime,
                           vacationTime=vacationTime, netAmount=netAmount, OTamount=OTamount)

@app.route("/users")
def users():
    if (not current_user):
        return redirect(url_for("login")) 
    users = User.query.all()
    return render_template('users.html', users=users)
    
    
def calcPayPeriod(period: float):
    period = round(period+.02, 2)
    week = (period - int(period))*100 # 0-52
    
    quarter = 0
    # Determine the quarter based on the payRate
    if (0 <= week < 13):
        quarter = 1
    elif (13 <= week < 26):
        quarter = 2
    elif (26 <= week < 39):
        quarter = 3
    elif (39 <= week < 53):
        quarter = 4
    else:
        quarter = 1
        period = int(period)+1
    
    return period, quarter, int(period)
    
@app.context_processor
def inject_functions():
    return dict(is_admin=is_admin)

def is_admin(user):
    if user.is_authenticated:
        return user.is_admin
    return False





@app.route('/time_requests', methods=['GET', 'POST'])
def time_requests():
    if request.method == 'POST':
        name = request.form['employeeName']
        date = request.form['timeOffDate']
        reason = request.form['reason']

        with open('requests.txt', 'a') as file:
            file.write(f'{name},{date},{reason}\n')

        return redirect(url_for('view_requests'))

    return render_template('timeRequests.html')

@app.route('/view_requests')
@login_required
def view_requests():
    requests = []
    with open('requests.txt', 'r') as file:
        for index, line in enumerate(file):
            name, date, reason = line.strip().split(',')
            requests.append({'id': index, 'name': name, 'date': date, 'reason': reason})
    return render_template('viewRequests.html', requests=requests, is_admin=current_user.is_admin)

@app.route('/update_request/<int:request_id>', methods=['POST'])
@login_required
def update_request(request_id):
    data = request.get_json()
    status = data.get('status')
    return jsonify({'success': True}), 200

# @app.route('/delete_request', methods=['POST'])
# def delete_request():
#     try:
#         request_id = int(request.form['id'])
#         with open('requests.txt', 'r') as file:
#             all_requests = file.readlines()
        
#         if 0 <= request_id < len(all_requests):
#             all_requests.pop(request_id)
        
#             with open('requests.txt', 'w') as file:
#                 file.writelines(all_requests)
        
#         return redirect(url_for('view_requests'))
    
#     except Exception as e:
#         return str(e), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

