#import liberaries
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
from wtforms import StringField, PasswordField, SubmitField, EmailField, IntegerField, DateField, HiddenField, SelectField, TextAreaField, BooleanField, RadioField, DateTimeField, TimeField
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
    
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.Integer, nullable=False)
    clinic_name = db.Column(db.String)
    clinic_num = db.Column(db.Integer)

    authenticated = db.Column(db.Boolean, default=False)

class Patient(db.Model):
    
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)
    email = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    phone_number = db.Column(db.Integer)
    adress = db.Column(db.String)
    birth_year = db.Column(db.Integer)
    medical_history = db.Column(db.String)
    ensurance_company = db.Column(db.String)

    def __repr__(self):
        return '<Name %r>' % self.name

class Operator(db.Model):

    __tablename__ = 'operator'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    gender = db.Column(db.String)
    phone_number = db.Column(db.Integer)
    speciality = db.Column(db.String)
    
    def __repr__(self):
        return '<Name %r>' % self.name

class Procedure(db.Model):

    __tablename__ = 'procdure'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_name = db.Column(db.String, db.ForeignKey('patient.name'))#, nullable=False) # changed from id to name 
    operator_id = db.Column(db.Integer, db.ForeignKey('operator.id'), nullable=False)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinic.id'))
    procedure_type = db.Column(db.String)
    tooth = db.Column(db.Integer)
    procedure_date = db.Column(db.Date)
    price = db.Column(db.Integer)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Name %r>' % self.id

class Clinic(db.Model):

    __tablename__ = 'clinic'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String, nullable=False)

    def __repr__(self):
        return '<Name %r>' % self.name

class Appointments(db.Model):

    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    patient_name = db.Column(db.String, db.ForeignKey('patient.name'))#, nullable=False) # changed from id to name 
    date = db.Column(db.Date)
    time = db.Column(db.Time)

    def __repr__(self):
        return '<Name %r>' % self.name

class Diagnosis(db.Model):
    __tablename__ = 'diagnosis'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    subject = db.Column(db.String)
    diagnosis =  db.Column(db.String)
    def __repr__(self):
        return '<Name %r>' % self.name
    
class Outcome(db.Model):
    __tablename__ = 'outcome'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    outcome_type = db.Column(db.String)
    outcome_date = db.Column(db.Date)
    amount = db.Column(db.Integer)
    description = db.Column(db.String)

    def __repr__(self):
        return '<Name %r>' % self.id

db.create_all()

#make the Form class
class UserForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    clinic_name = StringField('clinic_name')
    clinic_num = IntegerField('clinic_num')
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
    operator_name = SelectField('operator name')
    procedure_type = SelectField('procedure_type', choices=['endo', 'operative'])
    tooth = StringField('tooth')
    price = IntegerField('price')
    description = TextAreaField('description')
    selected_patient_name = HiddenField('selected_patient name')
    submit = SubmitField('submit')

class LoginForm(FlaskForm):
    email = EmailField('email', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    submit = SubmitField('submit')

class DiagnosisForm(FlaskForm):
    tooth = HiddenField('tooth')

class NameForm(FlaskForm):
    name = RadioField('n')
    submit = SubmitField('submit')

class HiddenNameForm(FlaskForm):
    selected_patient_name = HiddenField('selected_patient_name')
    submit = SubmitField('submit')


class AppointmentForm(FlaskForm):
    date = DateField('date')
    time = TimeField('time')
    selected_patient_name = HiddenField('selected_patient name')
    submit = SubmitField('submit')

class OperatorForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    gender = StringField('gender')
    phone = IntegerField('phone')
    speciality = StringField('speciality')
    
class ClinicForm(FlaskForm):
    name = StringField('name')

class OutcomeForm(FlaskForm):
    outcome_type = SelectField('outcome_type')
    amount = IntegerField('amount')
    description = StringField('description')



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
    patients = Patient.query.filter(Patient.user_id == flask_login.current_user.id)
    prices = db.session.query(Procedure.price).all()
    procedures = Procedure.query.filter(Procedure.user_id == flask_login.current_user.id)
    
    patient_list = []
    
    for patient in patients:
        patient_list.append(patient.name)

    #class NameForm(FlaskForm):
    #    name = RadioField('n')
    #    submit = SubmitField('submit')

    ################# FINANCIAL SYSTEM ##############
    #total income
    total_income = 0
    for procedure in procedures:
        total_income = int(total_income) + int(procedure.price)
    

    #last month income
    last_month_income = 0
    today = date.today()
    this_month = today.month
    this_year = today.year

    last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.user_id == flask_login.current_user.id)
    for procedure in last_month_procedures:
        last_month_income = int(last_month_income) + int(procedure.price)



    def income_this_month(procedure):
        last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.user_id == flask_login.current_user.id)
        income_last_month = 0
        for procedure in last_month_procedures:
            income_last_month = int(income_last_month) + int(procedure.price)
        return income_last_month

    def income_this_year(procedure):
        last_year_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, 1, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.user_id == flask_login.current_user.id)
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
    
    #waiting_list = WaitingPatients.query.filter(WaitingPatients.user_id == flask_login.current_user.id)
    form = NameForm()
    #this is hwo we pass data to the form from the route. or form.field.data = the_value
    form.name.choices = patient_list


    
    # show the upcoming appointments
    today_appointments = Appointments.query.order_by(Appointments.date).order_by(Appointments.time).filter(Appointments.user_id == flask_login.current_user.id).filter(Appointments.date == today )
    all_appointments = Appointments.query.order_by(Appointments.date).order_by(Appointments.time).filter(Appointments.user_id == flask_login.current_user.id).filter(Appointments.date > today )
    

    return render_template('admin_panil.html', patients = patients, total_income=total_income, prices=prices, procedures=procedures,
     last_month_income=last_month_income, income_from_endo=income_from_endo, income_from_operative=income_from_operative,
      income_from_bridge=income_from_bridge, income_from_crown=income_from_crown, income_from_implant=income_from_implant,
       income_from_scaling=income_from_scaling, income_from_surgery=income_from_surgery, income_from_other=income_from_other,
        income_from_endo_last_month=income_from_endo_this_month, income_from_operative_last_month=income_from_operative_this_month, 
        income_from_scaling_this_month=income_from_scaling_this_month, income_from_crown_this_month=income_from_crown_this_month, 
        income_from_bridge_this_month=income_from_bridge_this_month, income_from_implant_this_month=income_from_implant_this_month, 
        income_from_surgery_this_month=income_from_surgery_this_month, income_from_other_this_month=income_from_other_this_month, form=form,
        patient_list=patient_list, today_appointments=today_appointments, today=today,all_appointments=all_appointments)



@app.route('/reciption_panil', methods=['GET', 'POST'])
@flask_login.login_required
def reciption_panil():
    if request.method == 'POST':
        waiting_patient = request.form["waiting_patient"]
        day = date.today()
        user_id = flask_login.current_user.id

        #patient = WaitingPatients(name=waiting_patient, date=day, user_id=user_id)
        #db.session.add(patient)        
        #db.session.commit()
        
    patients = Patient.query.all().filter(Procedure.user_id == flask_login.current_user.id)

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
        user_id = flask_login.current_user.id

        name_with_id = name + str(flask_login.current_user.id)

        patient = Patient(name=name_with_id, gender=gender, birth_year=birth_year, adress=adress, email=email, phone_number=phone_number, medical_history=medical_history, user_id=user_id)
        db.session.add(patient)        
        db.session.commit()

        return redirect(url_for('admin_panil'))


    return render_template('add_new_patient.html', form=form)



@app.route('/patient_file', methods = ['GET', 'POST'])
def patient_file():
#get DATA from /admin_panil ###############################################################################################
    
    #provide form choises again here before submif the form
    patients = Patient.query.filter(Patient.user_id == flask_login.current_user.id)
    
    patient_list = []
    
    for patient in patients:
        patient_list.append(patient.name)

    name_form = NameForm()
    name_form.name.choices = patient_list
    if request.method == 'POST':
        selected_patient_name = request.form["name"]
        patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        patient_info = Patient.query.all()
        
        #make the hidden form and add the selected patient name to it to be supmitted
        hidden_form = HiddenNameForm()
        hidden_form.selected_patient_name.data = selected_patient_name

        

        
        

            #return redirect(url_for('patient_file'), patient_info = patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, patient_id=patient_id, operators=operators, procedure_form=procedure_form)
        
        patient_info = Patient.query.all()
        procedure_info = Procedure.query.all()
        operator_info = Operator.query.all()

    if name_form.validate_on_submit():
        selected_patient_name = name_form.name.data
        patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        patient_info = Patient.query.all()
        
        #make the hidden form and add the selected patient name to it to be supmitted
        hidden_form = HiddenNameForm()
        hidden_form.selected_patient_name.data = selected_patient_name

        

        
        

            #return redirect(url_for('patient_file'), patient_info = patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, patient_id=patient_id, operators=operators, procedure_form=procedure_form)
        
        patient_info = Patient.query.all()
        procedure_info = Procedure.query.all()
        operator_info = Operator.query.all()
        '''
        appointment_form = AppointmentForm()
        if appointment_form.validate_on_submit():
            date = appointment_form.date.data
            time = appointment_form.time.data
            patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
            appointment = Appointments(date=date, time=time, patient_id=patient_id)
            db.session.add(appointment)
            db.session.commit()
            patient_info = Patient.query.all()
            procedure_info = Procedure.query.all()
            operator_info = Operator.query.all()
            return render_template('patient_file.html', patient_info=patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name,
     patient_id=patient_id, operators=operators, procedure_form=procedure_form, hidden_form=hidden_form, operator_info=operator_info, appointment_form=appointment_form)
        '''

    return render_template('patient_file.html', patient_info=patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name,
     patient_id=patient_id, hidden_form=hidden_form, operator_info=operator_info)

    '''
        hidden_form = HiddenNameForm
        
        if hidden_form.validate_on_submit():

            selected_patient_name = name_form.name.data
            patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        
            procedure_types = ['Examination', 'Root canal treatment', 'Filling', 'Crown', 'Bridge', 'Scaling', 'Extraction', 'Implant', 'Surgery', 'Other']
            
            operators = Operator.query.filter(Operator.user_id == flask_login.current_user.id)
            
            operator_list = []
            
            for operator in operators:
                operator_list.append(operator.name)

            procedure_form = ProcedureForm()
            procedure_form.procedure_type.choices = procedure_types
            procedure_form.patient_name.data = selected_patient_name
            procedure_form.operator_name.choices = operator_list
            procedure_form.price.data = 0


            if procedure_form.validate_on_submit():
                operator_name = procedure_form.operator_name.data
                procedure_type = procedure_form.procedure_type.data
                tooth = procedure_form.tooth.data
                price = procedure_form.price.data
                selected_patient_name = procedure_form.patient_name.data
                description = procedure_form.description.data
                procedure_date = datetime.now()

                patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
                operator_id = db.session.query(Operator.id).filter(Operator.name == operator_name).scalar()

                

                #add the data to database
                procedure = Procedure(procedure_type=procedure_type, tooth=tooth, price=price, procedure_date=procedure_date, patient_id=patient_id, operator_id=operator_id, description=description)
                db.session.add(procedure)
                db.session.commit()

                flash('procedure added')
                return redirect(url_for('patient_file'), selected_patient_name=selected_patient_name)
        '''
    '''
        if request.method == 'GET':
            operator_name = request.args.get('operator_name')
            procedure_type = request.args.get('procedure_type')
            teeth = request.args.get('teeth')
            price = request.args.get('price')
            patient_name = request.args.get('patient_name')
            description = request.args.get('description')
            procedure_date = datetime.now()

            #get patient id 
            selected_patient_name = selected_patient_name
        
            patient_id = db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
            operator_id = db.session.query(Operator.id).filter(Operator.name == operator_name).scalar()

        

            #add the data to database
            procedure = Procedure(procedure_type=procedure_type, tooth=teeth, price=price, procedure_date=procedure_date, patient_id=patient_id, operator_id=operator_id, description=description)
            db.session.add(procedure)
            db.session.commit()

            flash('procedure added')
        '''

    
        
#                patient_info = Patient.query.all()
#                procedure_info = Procedure.query.all()
#                operators = Operator.query.all()
#                return render_template('patient_file.html', patient_info = patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name,
#                    patient_id=patient_id, operators=operators, procedure_form=procedure_form)
    
    #return render_template(url_for('patient_file'))


@app.route('/diagnosis', methods=['GET', 'POST'])
def diagnosis():
    if request.method == 'GET':
        patient_name = request.args.get('patient_name')
        #patient_name = request.form["patient_name"]
    
    
    if request.method == 'POST':
        #diagnosis =  request.form["diagnosis"] 
        diagnosis = request.form['diagnosis']
        subject = request.form["subject"]
        patient_name = request.form["patient_name"]
    
        patient_id = db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
    
        diagnosis = Diagnosis(diagnosis=diagnosis, subject=subject, patient_id=patient_id)
    
    return render_template('diagnosis.html', patient_name=patient_name)


@app.route('/added_procedure', methods = ['GET', 'POST'])
def added_procedure():
#get DATA from /patient_file

    hidden_form = HiddenNameForm()
    if hidden_form.validate_on_submit():
        selected_patient_name = hidden_form.selected_patient_name.data

        procedure_types = ['Examination', 'Root canal treatment', 'Filling', 'Crown', 'Bridge', 'Denture', 'Scaling', 'Extraction', 'Implant', 'Surgery', 'Other']
        operators = Operator.query.filter(Operator.user_id == flask_login.current_user.id)
        operator_list = []
            
        for operator in operators:
            #operator.name.strip('1234567890')
            operator_list.append(operator.name.strip('1234567890'))

        procedure_form = ProcedureForm()
        procedure_form.procedure_type.choices = procedure_types
        #procedure_form.patient_name.data = selected_patient_name
        procedure_form.operator_name.choices = operator_list
        procedure_form.selected_patient_name.data = selected_patient_name

        #procedure_form.price.data = 0

        patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        
        if procedure_form.validate_on_submit():
            operator_name = procedure_form.operator_name.data
            procedure_type = procedure_form.procedure_type.data
            tooth = procedure_form.tooth.data
            price = procedure_form.price.data
            selected_patient_name = procedure_form.selected_patient_name.data
            description = procedure_form.description.data
            operator_name_with_id = operator_name + str(flask_login.current_user.id)
            
            procedure_date = datetime.now()

            patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
            operator_id = db.session.query(Operator.id).filter(Operator.name == operator_name_with_id).scalar()

                

            #add the data to database
            procedure = Procedure(procedure_type=procedure_type, tooth=tooth, price=price, procedure_date=procedure_date, patient_name=selected_patient_name, operator_id=operator_id, description=description, user_id=flask_login.current_user.id)
            db.session.add(procedure)
            db.session.commit()

            hidden_form = HiddenNameForm()
            #hidden_form.selected_patient_name.data = selected_patient_name
            patient_info = Patient.query.all()
            procedure_info= Procedure.query.all()
            operator_info= Operator.query.all()
            return render_template('patient_file.html', patient_info=patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, patient_id=patient_id, operators=operators, procedure_form=procedure_form, hidden_form=hidden_form, operator_info=operator_info)

            #return render_template('added_procedure.html', selected_patient_name=selected_patient_name,  operator_id=operator_id, hidden_form=hidden_form, procedure_form=procedure_form, patient_id=patient_id, operator_name=operator_name)
        return render_template('added_procedure.html', selected_patient_name=selected_patient_name, hidden_form=hidden_form, procedure_form=procedure_form, patient_id=patient_id)


@app.route('/add_appointment', methods = ['GET', 'POST'])
def add_appointment():
#get DATA from /patient_file

    hidden_form = HiddenNameForm()
    if hidden_form.validate_on_submit():
        selected_patient_name = hidden_form.selected_patient_name.data

        appointment_form = AppointmentForm()
        appointment_form.selected_patient_name.data = selected_patient_name

        patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        
            #return render_template('added_procedure.html', selected_patient_name=selected_patient_name,  operator_id=operator_id, hidden_form=hidden_form, procedure_form=procedure_form, patient_id=patient_id, operator_name=operator_name)
        return render_template('add_appointment.html', selected_patient_name=selected_patient_name, hidden_form=hidden_form, patient_id=patient_id, appointment_form=appointment_form)



@app.route('/added_appointment', methods = ['GET', 'POST'])
def added_appointment():
#get DATA from /patient_file
        

        
        appointment_form = AppointmentForm()
        
        if appointment_form.validate_on_submit():
            date = appointment_form.date.data
            time = appointment_form.time.data
            selected_patient_name = appointment_form.selected_patient_name.data
            user_id = flask_login.current_user.id
            #patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
        
            #add the data to database
            appointment = Appointments(date=date, time=time, patient_name=selected_patient_name, user_id=user_id)
            db.session.add(appointment)
            db.session.commit()

            hidden_form = HiddenNameForm()
            #hidden_form.selected_patient_name.data = selected_patient_name
            patient_info = Patient.query.all()
            procedure_info= Procedure.query.all()
            operator_info= Operator.query.all()
            return render_template('patient_file.html', patient_info=patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, hidden_form=hidden_form, operator_info=operator_info)

            #return render_template('added_procedure.html', selected_patient_name=selected_patient_name,  operator_id=operator_id, hidden_form=hidden_form, procedure_form=procedure_form, patient_id=patient_id, operator_name=operator_name)
        return render_template('add_appointment.html',appointment_form=appointment_form)


'''
@app.route('/add_appointment', methods = ['GET', 'POST'])
def add_appointment():
    hidden_form = HiddenNameForm()
    if hidden_form.validate_on_submit():
        selected_patient_name = hidden_form.selected_patient_name.data
        patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()

        procedure_form = ProcedureForm

        appointment_form = AppointmentForm()
        appointment_form.selected_patient_name.data = selected_patient_name

        procedure_types = ['Examination', 'Root canal treatment', 'Filling', 'Crown', 'Bridge', 'Scaling', 'Extraction', 'Implant', 'Surgery', 'Other']
        operators = Operator.query.filter(Operator.user_id == flask_login.current_user.id)
        operator_list = []
            
        for operator in operators:
            operator_list.append(operator.name)
        
        if appointment_form.validate_on_submit():
            date = appointment_form.date.data
            time = appointment_form.time.data
            patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
            appointment = Appointments(date=date, time=time, patient_name=selected_patient_name)
            db.session.add(appointment)
            db.session.commit()

            hidden_form = HiddenNameForm()
            hidden_form.selected_patient_name.data = selected_patient_name
            patient_info = Patient.query.all()
            procedure_info= Procedure.query.all()
            operator_info= Operator.query.all()
        
            return render_template('patient_file.html', patient_info=patient_info, procedure_info=procedure_info, selected_patient_name=selected_patient_name, patient_id=patient_id, operators=operators, procedure_form=procedure_form, hidden_form=hidden_form, operator_info=operator_info)

        return render_template('add_appointment.html', appointment_form=appointment_form, selected_patient_name=selected_patient_name)
'''
'''
    if request.method == 'POST':
        operator_name = request.form['operator_name']
        procedure_type = request.form['procedure_type']
        teeth = request.form['teeth']
        price = request.form['price']
        patient_name = request.form['patient_name']
        description = request.form['description']
    procedure_date = datetime.now()

    #get patient id 
    
    
    patient_id = db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
    operator_id = db.session.query(Operator.id).filter(Operator.name == operator_name).scalar()

    

    #add the data to database
    procedure = Procedure(procedure_type=procedure_type, tooth=teeth, price=price, procedure_date=procedure_date, patient_id=patient_id, operator_id=operator_id, description=description)
    db.session.add(procedure)
    db.session.commit()

    patient_info = Patient.query.all()
'''
            #return render_template('added_procedure.html', patient_name=patient_name,  operator_id=operator_id)


@app.route('/add_new_doctor', methods=['GET', 'POST'])
def add_new_doctor():
    form = UserForm()

    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = form.password.data
        clinic_name = form.clinic_name.data
        clinic_num = form.clinic_num.data

        doctor = User(name=name, clinic_name=clinic_name, clinic_num=clinic_num, email=email, password=password)
        db.session.add(doctor)
        db.session.commit()
        flask_login.login_user(doctor)
        return redirect(url_for('admin_panil'))

    return render_template('add_new_doctor.html', form=form)

@app.route('/setup_account', methods=['GET', 'POST'])
def setup_account():
    operator_name = None
    operators = db.session.query(Operator.name).all()

    operator_form = OperatorForm()
    clinic_form = ClinicForm()

    if operator_form.validate_on_submit():
        operator_name = operator_form.name.data
        email = operator_form.email.data
        phone_number = operator_form.phone.data
        gender = operator_form.gender.data
        speciality = operator_form.speciality.data
        operator_name_with_id = operator_name + str(flask_login.current_user.id)

        operators = db.session.query(Operator.name).all()
        operator_list = []
        for operator in operators:
            operator_list.append(operator.name)

        if operator_name_with_id in operator_list:
            flash('operator already exist')
        else:
            operator= Operator(name=operator_name_with_id, email=email, phone_number=phone_number, gender=gender, speciality=speciality, user_id=flask_login.current_user.id)
            db.session.add(operator)
            db.session.commit()
            flash(f'{operator_name} added successfully as an operator in your clinic!')
   

    clinic_number = db.session.query(User.clinic_num).filter(User.id == flask_login.current_user.id).scalar()
    '''
    if clinic_form.validate_on_submit:
        name = clinic_form.name.data
        clinic = Clinic(name=name, user_id=flask_login.current_user.id)
        db.session.add(clinic)
        db.session.commit()

        flash('clinic added successfully')
    
    if request.method == 'Get':
        name = request.form['name']
        clinic = Clinic(name=name, user_id=flask_login.current_user.id)
        db.session.add(clinic)
        db.commit()

        flash('clinic added successfully')
    '''
        
    return render_template('setup_account.html', clinic_number=clinic_number, operator_name=operator_name, operator_form=operator_form,
     operators=operators, clinic_form=clinic_form)

@app.route('/added_room', methods=['GET', 'POST'])
def added_room():
    clinic_number = db.session.query(User.clinic_num).filter(User.id == flask_login.current_user.id).scalar()
    clinic_form = ClinicForm()
    if clinic_form.validate_on_submit:
        name = clinic_form.name.data
        clinic = Clinic(name=name, user_id=flask_login.current_user.id)
        db.session.add(clinic)
        db.session.commit()

        flash('clinic added successfully')
        return redirect('/admin_panil')
    
    if request.method == 'Post':
        name = request.form['name']
        clinic = Clinic(name=name, user_id=flask_login.current_user.id)
        db.session.add(clinic)
        db.commit()

        flash('clinic added successfully')
        return redirect('/admin_panil')


@app.route('/financials', methods=['GET', 'POST'])
def financials():
    form = OutcomeForm()
    outcome_type_list = ['Salary', 'Materials', 'Rent', 'Lab', 'Other']
    form.outcome_type.choices = outcome_type_list
    
    if form.validate_on_submit():
        outcome_type = form.outcome_type.data
        amount = form.amount.data
        description = form.description.data
        outcome_date = date.today()

        outcome = Outcome(outcome_type=outcome_type, amount=amount, description=description, outcome_date=outcome_date, user_id=flask_login.current_user.id)
        db.session.add(outcome)
        db.session.commit()

        flash('Outcome added successfully')

    outcome_list = Outcome.query.filter(Outcome.user_id == flask_login.current_user.id)




    #query data to choose the patient name to go ot patient file
    procedures = Procedure.query.filter(Procedure.user_id == flask_login.current_user.id)

    ################# FINANCIAL SYSTEM ##############
    #total income
    total_income = 0
    for procedure in procedures:
        total_income = int(total_income) + int(procedure.price)
    

    #last month income
    last_month_income = 0
    today = date.today()
    this_month = today.month
    this_year = today.year

    last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.user_id == flask_login.current_user.id)
    for procedure in last_month_procedures:
        last_month_income = int(last_month_income) + int(procedure.price)



    def income_this_month(procedure):
        last_month_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, this_month, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.user_id == flask_login.current_user.id)
        income_last_month = 0
        for procedure in last_month_procedures:
            income_last_month = int(income_last_month) + int(procedure.price)
        return income_last_month

    def income_this_year(procedure):
        last_year_procedures = Procedure.query.filter(Procedure.procedure_date > date(this_year, 1, 1)).filter(Procedure.procedure_type == procedure ).filter(Procedure.user_id == flask_login.current_user.id)
        income_last_year = 0
        for procedure in last_year_procedures:
            income_last_year = int(income_last_year) + int(procedure.price)
        return income_last_year
    
    #income from examination
    income_from_examination = income_this_year('Examination')

    #this month income from EXAMINATION
    income_from_examination_this_month = income_this_month('Examination')

    #this month income from DENTURE
    income_from_denture = income_this_year('Denture')

    #this month income from DENTURE
    income_from_denture_this_month = income_this_month('Denture')

    #income from ENDO
    income_from_endo = income_this_year('Root canal treatment')
    
    #this month income from ENDO 
    income_from_endo_this_month = income_this_month('Root canal treatment')

    #incoe from OPERATIVE 
    income_from_operative = income_this_year('Filling')

    #this month income from OPERATIVE
    income_from_operative_this_month = income_this_month('Filling')

    #income from SCALING
    income_from_scaling = income_this_year('Scaling')

    #this month income from SCALING
    income_from_scaling_this_month = income_this_month('Scaling')

    #income from CROWN
    income_from_crown = income_this_year('Crown')

    #this month income from CROWN
    income_from_crown_this_month = income_this_month('Crown')

    #income from BRIDGE
    income_from_bridge =income_this_year('Bridge')

    #this month income from BRIDGE
    income_from_bridge_this_month = income_this_month('Bridge')

    #income from IMPLANT
    income_from_implant = income_this_year('Implant')

    #this month income from IMPLANT
    income_from_implant_this_month = income_this_month('Implant')

    #income from SURGERY
    income_from_surgery = income_this_year('Surgery')

    #this month income from SARGERY
    income_from_surgery_this_month = income_this_month('Surgery')

    #income from OTHER
    income_from_other = income_this_year('Other')

    #this month income from OTHER
    income_from_other_this_month = income_this_month('Other')


    ############## Outcome ##########
    ## Month
    def outcome_this_month(type):
        last_month_outcome = Outcome.query.filter(Outcome.outcome_date > date(this_year, this_month, 1)).filter(Outcome.outcome_type == type ).filter(Outcome.user_id == flask_login.current_user.id)
        outcome_last_month = 0
        for outcome in last_month_outcome:
            outcome_last_month = int(outcome_last_month) + int(outcome.amount)
        return outcome_last_month

    salary_outcome_this_month = outcome_this_month('Salary')
    rent_outcome_this_month = outcome_this_month('Rent')
    materials_outcome_this_month = outcome_this_month('Materials')
    lab_outcome_this_month = outcome_this_month('Lab')
    other_outcome_this_month = outcome_this_month('Other')

    ## Year
    def outcome_this_year(type):
        last_year_outcome = Outcome.query.filter(Outcome.outcome_date > date(this_year, 1, 1)).filter(Outcome.outcome_type == type ).filter(Outcome.user_id == flask_login.current_user.id)
        outcome_last_year = 0
        for outcome in last_year_outcome:
            outcome_last_year = int(outcome_last_year) + int(outcome.amount)
        return outcome_last_year

    salary_outcome = outcome_this_year('Salary')
    rent_outcome = outcome_this_year('Rent')
    materials_outcome = outcome_this_year('Materials')
    lab_outcome = outcome_this_year('Lab')
    other_outcome = outcome_this_year('Other')

    last_month_outcome=0
    last_year_outcome=0

    last_year_outcome_table = Outcome.query.filter(Outcome.outcome_date > date(this_year, 1, 1)).filter(Outcome.user_id == flask_login.current_user.id)
    for outcome in last_year_outcome_table:
        last_year_outcome = int(last_year_outcome) + int(outcome.amount)


    last_month_outcome_table = Outcome.query.filter(Outcome.outcome_date > date(this_year, this_month, 1)).filter(Outcome.user_id == flask_login.current_user.id)
    for outcome in last_month_outcome_table:
        last_month_outcome = int(last_month_outcome) + int(outcome.amount)

    total_revenue_this_month = last_month_income - last_month_outcome
    total_revenue_this_year = total_income - last_year_outcome

    month_income_chart_list = [income_from_examination_this_month, income_from_endo_this_month, income_from_operative_this_month, 
    income_from_crown_this_month,income_from_bridge_this_month , income_from_scaling_this_month, income_from_surgery_this_month,
    income_from_implant_this_month, income_from_other_this_month]

    year_income_chart_list = [income_from_examination, income_from_endo, income_from_operative, 
    income_from_crown, income_from_bridge, income_from_scaling, income_from_surgery,
    income_from_implant, income_from_other_this_month]

    month_outcome_chart_list = [salary_outcome_this_month, rent_outcome_this_month, materials_outcome_this_month, lab_outcome_this_month, other_outcome_this_month]
    year_outcome_chart_list = [salary_outcome, rent_outcome, materials_outcome, lab_outcome, other_outcome]

    return render_template('financials.html', income_from_endo=income_from_endo, income_from_endo_this_month=income_from_endo_this_month,
    income_from_operative=income_from_operative, income_from_operative_this_month=income_from_operative_this_month,
    income_from_scaling=income_from_scaling, income_from_scaling_this_month=income_from_scaling_this_month, income_from_crown=income_from_crown,
    income_from_crown_this_month=income_from_crown_this_month,income_from_bridge=income_from_bridge,
    income_from_bridge_this_month=income_from_bridge_this_month, income_from_implant=income_from_implant,income_from_implant_this_month=income_from_implant_this_month,
    income_from_surgery=income_from_surgery, income_from_surgery_this_month=income_from_surgery_this_month,income_from_other=income_from_other, 
    income_from_other_this_month=income_from_other_this_month, total_income=total_income, last_month_income=last_month_income,
    income_from_examination=income_from_examination, income_from_examination_this_month=income_from_examination_this_month,
    income_from_denture=income_from_denture, income_from_denture_this_month=income_from_denture_this_month, form=form, 
    salary_outcome_this_month=salary_outcome_this_month, rent_outcome_this_month=rent_outcome_this_month, 
    materials_outcome_this_month=materials_outcome_this_month, lab_outcome_this_month=lab_outcome_this_month, other_outcome_this_month=other_outcome_this_month,
    salary_outcome=salary_outcome, rent_outcome=rent_outcome, materials_outcome=materials_outcome, lab_outcome=lab_outcome, other_outcome=other_outcome, 
    last_month_outcome=last_month_outcome, last_year_outcome=last_year_outcome, month_income_chart_list=month_income_chart_list,
    total_revenue_this_month=total_revenue_this_month, total_revenue_this_year=total_revenue_this_year, year_income_chart_list=year_income_chart_list,
    month_outcome_chart_list=month_outcome_chart_list, year_outcome_chart_list=year_outcome_chart_list)
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
- add doctor id to patient name- Done 
-add diagnosis
-add analysis
'''