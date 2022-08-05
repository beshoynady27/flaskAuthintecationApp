#import liberaries
from email.policy import default
from flask import Flask, render_template, redirect, request, url_for, session, flash
from flask_session import Session
from itertools import groupby
from datetime import datetime, date
import flask_login
from flask_sqlalchemy import SQLAlchemy
#liberaries for WTForms
from flask_wtf import FlaskForm
from pyparsing import And
from sqlalchemy import values
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, DateField, HiddenField, SelectField, TextAreaField
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

login_manager.login_view = "login"

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
    
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    phone_number = db.Column(db.Integer)
    adress = db.Column(db.String)
    birth_year = db.Column(db.Integer)
    medical_history = db.Column(db.String)

    def __repr__(self):
        return '<Name %r>' % self.name

class Procedure(db.Model):

    __tablename__ = 'procdure'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    procedure_type = db.Column(db.String)
    tooth = db.Column(db.Integer)
    procedure_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Name %r>' % self.name

class WaitingPatients(db.Model):
    __tablename__ = 'waiting_patients'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String)
    date = db.Column(db.Date)

    

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
    medical_history = TextAreaField('medical_hitory', default='Medically free')
    submit = SubmitField('submit')

class ProcedureForm(FlaskForm):
    procedure_type = SelectField('procedure_type', choices=['endo', 'operative'])
    tooth = IntegerField('tooth')
    price = IntegerField('price')
    submit = SubmitField('submit')

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')

#class LobbyForm(FlaskForm):
#    patients_waiting = s

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
        if user:
            flask_login.login_user(user, remember=True)
        else:
            return redirect(url_for('index'))
        return redirect(url_for('choose_panil'))

    return render_template('login.html', form=form, email=email)


@app.route('/choose_panil')
@flask_login.login_required
def choose_panil():

    return render_template('choose_panil.html')


@app.route('/logout')
@flask_login.login_required
def logout():
    flask_login.logout_user()
    return redirect('/')


@app.route('/admin_panil', methods=['GET', 'POST'])
@flask_login.login_required
def admin_panil():
    #query data to choose the patient name to go ot patient file
    patients = Patient.query.filter(Patient.doctor_id == flask_login.current_user.id)
    prices = db.session.query(Procedure.price).all()
    procedures = Procedure.query.filter(Procedure.doctor_id == flask_login.current_user.id)
    

    ################# FINANCIAL SYSTEM ##############
    #total income
    total_income = 0
    for procedure in procedures:
        total_income = int(total_income) + int(procedure.price)
    

    #last month income
    last_month_income = 0
    today = datetime.today()
    this_month = today.month
    this_year = today.year
    last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.doctor_id == flask_login.current_user.id)
    for procedure in last_month_procedures:
        last_month_income = int(last_month_income) + int(procedure.price)



    def income_this_month(procedure):
        last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.doctor_id == flask_login.current_user.id)
        income_last_month = 0
        for procedure in last_month_procedures:
            income_last_month = int(income_last_month) + int(procedure.price)
        return income_last_month

    def income_this_year(procedure):
        last_year_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, 1, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.doctor_id == flask_login.current_user.id)
        income_last_year = 0
        for procedure in last_year_procedures:
            income_last_year = int(income_last_year) + int(procedure.price)
        return income_last_year


    #income from ENDO
    income_from_endo = income_this_year('endo')
    
    #this month income from ENDO 
    income_from_endo_this_month = income_this_month('endo')

    #incoe from OPERATIVE 
    income_from_operative = income_this_year('operative')

    #this month income from OPERATIVE
    income_from_operative_this_month = income_this_month('operative')

    #income from SCALING
    income_from_scaling = income_this_year('scaling')

    #this month income from SCALING
    income_from_scaling_this_month = income_this_month('scaling')

    #income from CROWN
    income_from_crown = income_this_year('crown')

    #this month income from CROWN
    income_from_crown_this_month = income_this_month('crown')

    #income from BRIDGE
    income_from_bridge =income_this_year('bridge')

    #this month income from BRIDGE
    income_from_bridge_this_month = income_this_month('bridge')

    #income from IMPLANT
    income_from_implant = income_this_year('implant')

    #this month income from IMPLANT
    income_from_implant_this_month = income_this_month('implant')

    #income from SURGERY
    income_from_surgery = income_this_year('surgery')

    #this month income from SARGERY
    income_from_surgery_this_month = income_this_month('surgery')

    #income from OTHER
    income_from_other = income_this_year('other')

    #this month income from OTHER
    income_from_other_this_month = income_this_month('other')


    ########### LOBBY ######
    
    waiting_list = WaitingPatients.query.filter(WaitingPatients.doctor_id == flask_login.current_user.id)


    return render_template('admin_panil.html', patients = patients, total_income=total_income, prices=prices, procedures=procedures,
     last_month_income=last_month_income, income_from_endo=income_from_endo, income_from_operative=income_from_operative,
      income_from_bridge=income_from_bridge, income_from_crown=income_from_crown, income_from_implant=income_from_implant,
       income_from_scaling=income_from_scaling, income_from_surgery=income_from_surgery, income_from_other=income_from_other,
        income_from_endo_last_month=income_from_endo_this_month, income_from_operative_last_month=income_from_operative_this_month, 
        income_from_scaling_this_month=income_from_scaling_this_month, income_from_crown_this_month=income_from_crown_this_month, 
        income_from_bridge_this_month=income_from_bridge_this_month, income_from_implant_this_month=income_from_implant_this_month, 
        income_from_surgery_this_month=income_from_surgery_this_month, income_from_other_this_month=income_from_other_this_month, waiting_list=waiting_list)



@app.route('/reciption_panil', methods=['GET', 'POST'])
@flask_login.login_required
def reciption_panil():
    if request.method == 'POST':
        waiting_patient = request.form["waiting_patient"]
        day = date.today()
        doctor_id = flask_login.current_user.id

        patient = WaitingPatients(name=waiting_patient, date=day, doctor_id=doctor_id)
        db.session.add(patient)        
        db.session.commit()
        
    patients = Patient.query.all().filter(Procedure.doctor_id == flask_login.current_user.id)

    return render_template('reception_panil.html', patients=patients)



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
        medical_history = form.medical_history.data
        doctor_id = flask_login.current_user.id

        name_with_id = name + str(flask_login.current_user.id)

        patient = Patient(name=name_with_id, gender=gender, birth_year=birth_year, adress=adress, email=email, phone_number=phone_number, medical_history=medical_history, doctor_id=doctor_id)
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
    procedure_date = datetime.today()
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
    
    return render_template('added_procedure.html', patient_name=patient_name)


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
- fix the add second procedure - DONE
- add button to remove patient - 
- fix the login - DONE
- fix the session 
- reception panil 
    -waiting patinta - Done
    -add new patient - Done
    - add payment 
- add doctor id to patient name
-add diagnosis
'''