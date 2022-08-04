#import liberaries
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_session import Session
from itertools import groupby
from datetime import datetime
import flask_login
from flask_sqlalchemy import SQLAlchemy
#liberaries for WTForms
from flask_wtf import FlaskForm
from sqlalchemy import values
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, DateField, HiddenField
from wtforms.validators import DataRequired, email, length, Length

#configure app
app = Flask(__name__)

#configur secret key
app.config['SECRET_KEY'] = 'secret_key'

#configure sessions
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


login_manager = flask_login.LoginManager()
login_manager.init_app(app)

#login_manager.login_view = "users.login"

#adress to database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///LASTdatabase.db'

# initialize SQLAlchemy
db = SQLAlchemy(app)


#make the tables in the database 
class User(db.Model, flask_login.UserMixin):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String)
    speciality = db.Column(db.String)
    authenticated = db.Column(db.Boolean, default=False)

    '''
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
    '''

class Patient(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
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
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    procedure_type = db.Column(db.String)
    tooth = db.Column(db.Integer)
    procedure_date = db.Column(db.DateTime)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name
db.create_all()

#make the Form class
class UserForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    gender = StringField('gender')
    speciality = StringField('gender')
    submit = SubmitField('submit')
    submit = SubmitField('submit')

class PatientForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    gender = StringField('gender')
    phone_number = IntegerField('phone_number')
    adress = StringField('adress')
    birth_year = IntegerField('birth_year')
    submit = SubmitField('submit')

class ProcedureForm(FlaskForm):
    procedure_type = StringField('procedure_type')
    tooth = IntegerField('tooth')
    price = IntegerField('price')
    #patient_name = HiddenField('patient_name')
    submit = SubmitField('submit')

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')

@login_manager.user_loader
def user_loader(user_id):
    
    return User.query.get(user_id)



@app.route('/')
def index():

    return render_template('index.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    email = None
    password = None
    if form.validate_on_submit():

        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email = email, password = password).first()
        flask_login.login_user(user, remember=True)

        return redirect(url_for('admin_panil'))

    return render_template('login.html', form=form, email=email)


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('/')


@app.route('/admin_panil')
@flask_login.login_required
def admin_panil():
    #query data to choose the patient name to go ot patient file
    patients = Patient.query.all()
    prices = db.session.query(Procedure.price).all()
    procedures = Procedure.query.all()
    total_revnue = 0
    for procedure in procedures:
        total_revnue = int(total_revnue) + int(procedure.price)
    return render_template('admin_panil.html', patients = patients, total_revnue=total_revnue, prices=prices, procedures=procedures)


@app.route('/add_new_patient', methods=['GET', 'POST'])
def add_new_patient():
    form = PatientForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        adress = form.adress.data
        phone_number = form.phone_number.data
        gender = form.gender.data
        birth_year = form.birth_year.data

        patient = Patient(name=name, gender=gender, birth_year=birth_year, adress=adress, email=email, phone_number=phone_number)
        db.session.add(patient)        
        db.session.commit()

        return redirect(url_for('admin_panil'))


    return render_template('add_new_patient.html', form=form)



@app.route('/patient_file', methods = ['GET', 'POST'])
def patient_file():
#get DATA from /admin_panil
    if request.method == 'POST':
        selected_patient_name = request.form["n"]
    patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
    procedure_date = datetime.now()
    form = ProcedureForm()
    '''
    if form.validate_on_submit():
        procedure_type = form.procedure_type.data
        tooth = form.tooth.data
        price = form.price.data

        #procedure_date = datetime.now()
        #patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        
        procedure = Procedure(procedure_type=procedure_type, tooth=tooth, price=price, procedure_date=procedure_date, patient_id=patient_id)
        db.session.add(procedure)
        db.session.commit()
        
        return redirect(url_for('admin_panil'))
        #selected_patient_name = request.form["n"]
        #session['selected_patient_name'] =  selected_patient_name
    #session["name"] = db.session.query(Patient.name).filter(Patient.name == selected_patient_name)
    #session['test'] = 'value'
    #if selected_patient_name not in session[ 'global_patient_name' ]:
     #   session[ 'global_patient_name' ] = selected_patient_name
    '''
    patient_info = Patient.query.all()
    procedure_info = Procedure.query.all()
    return render_template('patient_file.html',form=form, patient_info = patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, patient_id=patient_id)


@app.route('/added_procedure', methods = ['GET', 'POST'])
def added_procedure():
#get DATA from /patient_file
    if request.method == 'POST':
        procedure_type = request.form['procedure_type']
        teeth = request.form['teeth']
        price = request.form['price']
        patient_name = request.form['patient_name']
    procedure_date = datetime.now()

        
    
    global_patient_name = session.get('selected_patient_name', None)
    my_var = session.get('test',None)
    #get patient id 
    
    patient_id = db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
    doctor_id = flask_login.current_user.id 

    #add the data to database
    procedure = Procedure(procedure_type=procedure_type, tooth=teeth, price=price, procedure_date=procedure_date, patient_id=patient_id, doctor_id=doctor_id)
    db.session.add(procedure)
    db.session.commit()

    patient_info = Patient.query.all()
    
    return render_template('patient_file_after_added_procedure.html', patient_info = patient_info, patient_id=patient_id, global_patient_name=global_patient_name, my_var=my_var)


@app.route('/add_new_doctor', methods=['GET', 'POST'])
def add_new_doctor():
    form = UserForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        gender = form.gender.data
        speciality = form.speciality.data

        doctor = User(name=name, gender=gender, speciality=speciality, email=email, password=password)
        db.session.add(doctor)
        db.session.commit()
        flask_login.login_user(doctor)
        return redirect(url_for('admin_panil'))

    return render_template('add_new_doctor.html', form=form)

    

'''
TODO :
- validate the new patient name does not exist in the database - DONE
- fix the add second procedure
- add button to remove patient - 
- fix the login - 
- fix the session 
'''