
import email
from unicodedata import name
from unittest import result
from flask import Flask, render_template, redirect, request, url_for
from itertools import groupby
from datetime import datetime
import flask_login
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

#function to connect to database



app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ndatabase.db'
db = SQLAlchemy(app)
#to make SQLAlchemy connect to the database
#engine = create_engine('sqlite:///ndatabase', echo=True)

#...
#make the tables in the database 
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
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    procedure_type = db.Column(db.String)
    tooth = db.Column(db.Integer)
    procedure_date = db.Column(db.DateTime)
    price = db.Column(db.Integer)

    def __repr__(self):
        return '<Name %r>' % self.name
db.create_all()



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
#@flask_login.login_required
def admin_panil():

    patients = Patient.query.all()
    return render_template('admin_panil.html', patients = patients)

@app.route('/add_new_patient')
def add_new_patient():

    return render_template('add_new_patient.html')


#recieve the supmetted form add_new_patient.html and add the results to the database
@app.route('/added_patient', methods=["GET", "POST"])
def added_patient():

    patient_name = request.form['patient_name']
    gender = request.form['gender']
    birth_year = request.form['birth_year']
    adress = request.form['adress']
    phone_number = request.form['phone_number']
    email = request.form['email']
    ######################################################################################
    #validate patient name dose not exist in the database 
    patients = Patient.query.all()
    existing_patient_names ='testtt'

    #for a in patients:
        #existing_patient_names.append(a.name)
    #patient_names = patients.name
    if patient_name not in patients:
        patient = Patient(name=patient_name, gender=gender, birth_year=birth_year, adress=adress, email=email, phone_number=phone_number)
        db.session.add(patient)
        db.session.commit()
    ######################################################################################
    '''
    ins = Patient.insert()
    conn = engine.connect()
    result = conn.execute(ins)
    '''
    return redirect('/admin_panil',existing_patient_names=existing_patient_names,patients=patients)


@app.route('/patient_file', methods = ['GET', 'POST'])
def patient_file():
    if request.method == 'POST':
        selected_patient_name = request.form["n"]
       # procedure_type = request.form['procedure_type']
        #teeth = request.form['teeth']
       # price = request.form['price']
    #patient_id = db.session.query(Patient.id).filter(Patient.name == selected_patient_name).scalar()
    patient_info = Patient.query.all()

    #cur.execute('INCERT INTO procedures(procedure_type, teeth, price) VALUES(?, ?, ?);',(procedure_type, teeth, price))
   # patient_info= cur.execute('SELECT * FROM patients ')
   # patient_info= cur.execute('SELECT * FROM patients WHERE patient_name = (?);', (selected_patient_name,))


    return render_template('patient_file.html', patient_info = patient_info, selected_patient_name=selected_patient_name)


@app.route('/added_procedure', methods = ['GET', 'POST'])
def added_procedure():
    if request.method == 'POST':
        procedure_type = request.form['procedure_type']
        teeth = request.form['teeth']
        price = request.form['price']
        patient_name = request.form['patient_name']
        procedure_date = datetime.now()
    
    #get patient id 
    #patient_id = Patient.id.query.filter_by(name = patient_name).first()
    #patient_id =1# db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
    patient_id = db.session.query(Patient.id).filter(Patient.name == patient_name).scalar()
    #add the data to database
    procedure = Procedure(procedure_type=procedure_type, tooth=teeth, price=price, procedure_date=procedure_date, patient_id=patient_id)
    
    db.session.add(procedure)
    db.session.commit()

    patient_info = Patient.query.all()
    '''
    patient_id = cur.execute('SELECT id FROM patients WHERE patient_name = (?);', (patient_name,)).fetchone()['id']
    cur.execute('INSERT INTO procedures(procedure_type, tooth, price, procedure_date, patient_id) VALUES(?, ?, ?, ?, ?);',
                                                                        (procedure_type, teeth, price, prucedure_date, patient_id))
    patient_info= cur.execute('SELECT * FROM patients WHERE patient_name = (?);', (patient_name,))
    '''
    




    return render_template('patient_file_after_added_procedure.html', patient_info = patient_info, patient_id=patient_id)


@app.route('/add_new_doctor')
def add_new_doctor():

    return render_template('add_new_doctor.html')

@app.route('/added_doctor', methods= ['GET', 'POST'])
def added_doctor():
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        speciality = request.form['speciality']
        email = request.form['email']
        password = request.form['doctor_password']
    
    doctor = User(name=name, gender=gender, speciality=speciality, email=email, password=password)
    db.session.add(doctor)
    db.commit()
    '''
    cur.execute('INSERT INTO doctors (doctor_name, gender, speciality, email, doctor_password) VALUES(?, ?, ?, ?, ?)',
                    (name, gender, speciality, email, password))
    '''


    return redirect('/admin_panil')

    

'''
TODO :
- validate the new patient name does not exist in the database
- add button to remove patient 
- fix the login 
'''