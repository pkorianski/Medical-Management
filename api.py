# Title: WellFrame Tech Challenge API
# Created by: Patrick M. Korianski
# Version: 1.0

# Imports
from flask import Flask, request, render_template
from sqlalchemy import create_engine
from json import dumps
import json

# Variables
global patient_name

# Using SQLAlchemy to access the health.db database
# Connecting to the DB will be crutial to inserting, receiving, and delete patient/medical data
db_connect = create_engine('sqlite:///health.db')

# Initializing Flask framework and API
app = Flask(__name__, template_folder='templates')

#################
## API Methods ##
#################

# Request to start the web app homepage
@app.route('/')
def home():
    return render_template('index.html')

# Get request to view the current medication list in the heath.db
@app.route('/view_meds.html', methods=['GET'])
def get_meds():
    conn = db_connect.connect()
    query = conn.execute("select * from available_medicines order by medicine_name")
    data = [i for i in query.cursor.fetchall()]
    return render_template('view_meds.html', medicines=json.loads(json.dumps(data)))

# Get request to view the current patient list in the health.db
@app.route('/view_patients.html', methods=['GET'])
def get_patients():
    conn = db_connect.connect()
    query = conn.execute("select * from patients order by patient_name")
    data = [i for i in query.cursor.fetchall()]
    return render_template('view_patients.html', patients=json.loads(json.dumps(data)))

# Get request to view the current patient/medication list in the health.db
@app.route('/view_patmeds.html', methods=['GET'])
def get_patmeds():
    conn = db_connect.connect()
    query = conn.execute("select * from patient_meds order by patient_name, medicine_name")
    data = [i for i in query.cursor.fetchall()]
    return render_template('view_patmeds.html', patmeds=json.loads(json.dumps(data)))

# Get request to get the current patients and medicines to use to add medications to patients
@app.route('/patients_addmed.html', methods=['GET'])
def get_addmed_data():
    conn = db_connect.connect()
    pat_query = conn.execute("select * from patients order by patient_name")
    med_query = conn.execute("select * from available_medicines order by medicine_name")
    pat_data  = [i for i in pat_query.cursor.fetchall()]
    med_data  = [i for i in med_query.cursor.fetchall()]
    return render_template('patients_addmed.html', patients=json.loads(json.dumps(pat_data)), medicines=json.loads(json.dumps(med_data)))

# Get request to receive current patients in the delete medication process
@app.route('/patients_delmed.html', methods=['GET'])
def get_delpat_data():
    conn = db_connect.connect()
    pat_query = conn.execute("select * from patients order by patient_name")
    pat_data  = [i for i in pat_query.cursor.fetchall()]
    return render_template('patients_delmed.html', pat=json.loads(json.dumps([])),patients=json.loads(json.dumps(pat_data)), medicines=json.loads(json.dumps([])))

# Post request to add new medicine to the availabe_medicines table in health.db
@app.route('/add_med', methods=['POST'])
def post_meddata():
    med =  request.form['mname']
    conn = db_connect.connect()
    try:
        conn.execute('insert into available_medicines (medicine_name) values ("{}")'.format(med))
    except:
        return render_template('/index.html', message='ERROR: Could not insert "{}" into the Medicine list. Try another medicine name'.format(med))
    return render_template('/index.html', message='SUCCESS: Added "{}" to the Medicine list.'.format(med))

# Post request to add new patient to the patients table in health.db
@app.route('/add_patient', methods=['POST'])
def post_patdata():
    pat = request.form['pname']
    conn = db_connect.connect()
    try:
        conn.execute('insert into patients (patient_name) values ("{}")'.format(pat))
    except:
        return render_template('/index.html', message='ERROR: Could not insert "{}" into the Patients list. Try another patient name.'.format(pat))
    return render_template('/index.html', message='SUCCESS: Added "{}" to the Patients list.'.format(pat))

# Post request to add new medicine to a patient
@app.route('/patient_addmed', methods=['POST'])
def post_pataddmed():
    pat = request.form['pname']
    med = request.form['mname']
    conn = db_connect.connect()
    try:
        conn.execute('insert into patient_meds (patient_name,medicine_name) values ("{}","{}")'.format(pat,med))
    except:
        return render_template('/index.html', message='ERROR: Could not add "{}" medicine to patient "{}".'.format(med,pat))
    return render_template('/index.html', message='SUCCESS: Added "{}" medicine to patient "{}".'.format(med,pat))

# POST request that receives the selected patient from the web app and then query's the patient_meds db to find the patients current medications
@app.route('/patient_delmed1', methods=['POST'])
def get_pat():
    pat = request.form['pname']
    global patient_name
    patient_name = pat
    conn = db_connect.connect()
    try:
        med_query = conn.execute('select medicine_name from patient_meds where patient_name ="{}" order by medicine_name'.format(pat))
        med_data  = [i for i in med_query.cursor.fetchall()]
        pat_data  = [[str(pat)]]
        return render_template('patients_delmed.html', patients=json.loads(json.dumps(pat_data)), medicines=json.loads(json.dumps(med_data)))
    except:
        return render_template('/index.html', message='ERROR: Could not select from patient_meds table with patient "{}"'.format(pat))

# POST request (since HTML forms don't allow DELETE methods in HTML5) to delete a medicine from a patient
@app.route('/patient_delmed2', methods=['POST'])
def delete_medpat():
    try:
        med = request.form['mname']
        conn = db_connect.connect()
        conn.execute('delete from patient_meds where patient_name="{}" and medicine_name="{}"'.format(patient_name,med))
        return render_template('/index.html', message='SUCCESS: Deleted "{}" medicine from patient "{}"'.format(med,patient_name))
    except:
        return render_template('/index.html', message='ERROR: Could not delete medication. Please select patient, click "Get Medications", and select medication.')

# Running flask web framework application
if __name__ == '__main__':
    app.run(port=5000)
