
import email
import sqlite3
from flask import Flask, render_template, redirect, request, url_for
from itertools import groupby
from datetime import datetime
import flask_login
#from flask_sqlalchemy import SQLAlchemy

#function to connect to database

def get_db_connection() :
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
#app.config('SECRET_KEY') = 'secret_key'


login_manager = flask_login.LoginManager()
login_manager.init_app(app)




conn = get_db_connection()
cur = conn.cursor()
users = cur.execute('select * FROM doctors')
cur.close()

from flask_sqlalchemy import SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
db.create_all()
#...

class User(db.Model):
    """An admin user capable of viewing reports.

    :param str email: email address of user
    :param str password: encrypted password for the user

    """
    __tablename__ = 'user'

    email = db.Column(db.String, primary_key=True)
    password = db.Column(db.String)
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

    
    conn = get_db_connection()
    cur = conn.cursor()
    patients = cur.execute('select * from patients')
    
    

    return render_template('admin_panil.html', patients = patients)

@app.route('/add_new_patient')
def add_new_patient():

    return render_template('add_new_patient.html')


#recieve the supmetted form add_new_patient.html and add the results to the database
@app.route('/added_patient', methods=["GET", "POST"])
def added_patient():
    conn = get_db_connection()

    patient_name = request.form['patient_name']
    gender = request.form['gender']
    birth_year = request.form['birth_year']
    adress = request.form['adress']
    phone_number = request.form['phone_number']
    email = request.form['email']

    cur = conn.cursor()
    cur.execute('INSERT INTO patients (patient_name, gender, birth_year, adress, phone_number, email) VALUES(?, ?, ?, ?, ?, ?)',
                    (patient_name, gender, birth_year, adress, phone_number, email))
    conn.commit()
    conn.close()

    return redirect('/admin_panil')


@app.route('/patient_file', methods = ['GET', 'POST'])
def patient_file():
    if request.method == 'POST':
        selected_patient_name = request.form["n"]
       # procedure_type = request.form['procedure_type']
        #teeth = request.form['teeth']
       # price = request.form['price']


    
    conn = get_db_connection()
    cur = conn.cursor()
    #cur.execute('INCERT INTO procedures(procedure_type, teeth, price) VALUES(?, ?, ?);',(procedure_type, teeth, price))
   # patient_info= cur.execute('SELECT * FROM patients ')
    patient_info= cur.execute('SELECT * FROM patients WHERE patient_name = (?);', (selected_patient_name,))


    return render_template('patient_file.html', patient_info = patient_info, selected_patient_name=selected_patient_name)


@app.route('/added_procedure', methods = ['GET', 'POST'])
def added_procedure():
    if request.method == 'POST':
        procedure_type = request.form['procedure_type']
        teeth = request.form['teeth']
        price = request.form['price']
        patient_name = request.form['patient_name']
        prucedure_date = datetime.now()
    conn = get_db_connection()
    cur = conn.cursor()
    patient_id = cur.execute('SELECT id FROM patients WHERE patient_name = (?);', (patient_name,)).fetchone()['id']
    cur.execute('INSERT INTO procedures(procedure_type, tooth, price, procedure_date, patient_id) VALUES(?, ?, ?, ?, ?);',
                                                                        (procedure_type, teeth, price, prucedure_date, patient_id))
    patient_info= cur.execute('SELECT * FROM patients WHERE patient_name = (?);', (patient_name,))
    conn.commit()
    




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

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO doctors (doctor_name, gender, speciality, email, doctor_password) VALUES(?, ?, ?, ?, ?)',
                    (name, gender, speciality, email, password))
    conn.commit()
    conn.close()      
    
    


    return redirect('/admin_panil')

    