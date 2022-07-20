
import email
from flask import Flask, render_template, redirect, request, url_for
from itertools import groupby
from datetime import datetime
import flask_login
from flask_sqlalchemy import SQLAlchemy

#function to connect to database



app = Flask(__name__)
#app.config('SECRET_KEY') = 'secret_key'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ndatabase.db'
db = SQLAlchemy(app)
db.create_all()
#...

class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    grnder = db.Column(db.String)
    speciality = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False


class Patient(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    phone_number = db.Column(db.Integer)
    adress = db.Column(db.String)
    birth_year = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name



class Procedure(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'procdure'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer)
    procedure_type = db.Column(db.String)
    tooth = db.Column(db.Integer)
    procedure_date = db.Column(db.DateTime)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated User object.

    :param unicode user_id: user_id (email) user to retrieve

    """
    return User.query.get(user_id)




@app.route('/')
def index():

    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():

    return render_template('login.html')

@app.route('/loged_in', methods=["GET", "POST"])
def loged_in() :
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['doctor_password']
    user = User(email = email, password = password)
    db.session.add(user)
    db.session.commit()
    if user:
        if True:
            user.authenticated = True
            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user, remember=True)
            
    '''
    if email in users :
        user = User()
        user.id = email
        flask_login.login_user(user)'''

    return redirect('/admin_panil')

@app.route('/admin_panil')
@flask_login.login_required
def admin_panil():

    return render_template('admin_panil.html', '''patients = patients''')