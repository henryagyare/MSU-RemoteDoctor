from flask import Flask, render_template, request, redirect, url_for, jsonify,  session, flash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import cast
from sqlalchemy.types import String

import os

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

#configuration of sqlalchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patients_data.db' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# UserAccount Class
class UserAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)  # Consider hashing this in production
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    role = db.Column(db.String(50), nullable=False)

# Patients Class
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(300))
    age = db.Column(db.Integer)
    sex = db.Column(db.String(300))
    arrival = db.Column(db.Integer)
    systolic = db.Column(db.Integer)
    diastolic = db.Column(db.Integer)
    heart_rate = db.Column(db.Integer)
    temperature = db.Column(db.Integer)    
    oxygen_saturation = db.Column(db.Integer)
    glucose = db.Column(db.Integer)
    current_medications = db.Column(db.String(300))
    allergies = db.Column(db.String(300))
    stroke_history = db.Column(db.String(500))
    medical_history = db.Column(db.String(500))
    radiologist_notes = db.Column(db.String(500))
    nhiss_score = db.Column(db.Integer)
    diagnosis = db.Column(db.String(500))
    treatment = db.Column(db.String(500))
    neuro_approved = db.Column(db.Boolean, default=False)
    ct_scan_filename = db.Column(db.String(255))

#appointment scheduling with neurologists. 
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    datetime = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(300), nullable=False)
    notes = db.Column(db.String(500))
    status = db.Column(db.String(50), default='Scheduled')

    patient = db.relationship('Patient', backref='appointments')

with app.app_context():
    db.create_all

patient_data_list = [        
        {"id": 1, "fullname": "John Doe", "age": 45, "arrival": "10:30 AM", "heart_rate": 78, "status": "Stable"},
        {"id": 2, "fullname": "Jane Smith", "age": 52, "arrival": "11:15 AM", "heart_rate": 92, "status": "Critical"},
        {"id": 3, "fullname": "Samuel Green", "age": 36, "arrival": "9:50 AM", "heart_rate": 85, "status": "Stable"},
]
patient_data = {}

@app.route("/")
def home():
    return redirect(url_for("login"))

# Dummy users dictionary for demonstration. Users credentials will be later sourced from the database
users = {
    'HenryAsante': {'password': 'nurse1234', 'role': 'technician'},
    'ChrisGadze': {'password': 'neuro2234', 'role': 'neurologist'},
    'JosephAuthur': {'password': 'patient2345', 'role': 'patient'}
}

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")  # show form on GET

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role').lower()  # normalize role

        user = users.get(username)


        if user and user['password'] == password and user['role'] == role:
            if role == 'technician':
                return redirect(url_for('technician_dashboard'))
            elif role == 'neurologist':
                return redirect(url_for('neurologist_dashboard'))
            elif role == 'patient':
                return redirect(url_for('patient_data_display'))
           
            else:
                return "Role not recognized."
        else:
            return "Invalid Credentials or Role Mismatch!"


@app.route('/technician_dashboard', methods=["GET", "POST"])
def technician_dashboard():
    if request.method == "POST":
        if "reset" in request.form:
            all_patients = Patient.query.order_by(Patient.id.desc()).all()
        else:
            search_query = request.form.get("search_query", "")
            all_patients = Patient.query.filter(
                (Patient.fullname.ilike(f"%{search_query}%")) |
                (cast(Patient.age, db.String).ilike(f"%{search_query}%"))
            ).order_by(Patient.id.desc()).all()
    else:
        all_patients = Patient.query.order_by(Patient.id.desc()).all()

    return render_template('technician_dashboard.html', all_patients=all_patients)


@app.route('/neurologist_dashboard')
def neurologist_dashboard():
    new_patients = Patient.query.count()
    patients = Patient.query.order_by(Patient.id.desc()).limit(10).all()
    appointments = Appointment.query.filter_by(status='Scheduled').order_by(Appointment.datetime.asc()).limit(10).all()
    upcoming_appointments_count = Appointment.query.filter_by(status='Scheduled').count()
    alerts=0 

    

    return render_template(
        'neurologist_dashboard.html',
        new_patients=new_patients,
        alerts=alerts,
        patients=patients,
        appointments = appointments,
        upcoming_appointments=upcoming_appointments_count,
    )

    
@app.route('/patient_data_entry')
def patient_data_entry():
    return render_template("patient_data_entry.html")

app.secret_key = 'asdfghjkl123456789' 

@app.route('/confirm_page', methods=["POST"])
def confirm_page():
    nhiss_score = request.form.get("nhiss_score")
    session['nhiss_score'] = nhiss_score
    return render_template("confirm_page.html", nhiss_score=nhiss_score)

@app.route('/nhiss_score', methods=["POST"])
def nhiss_score():
    nhiss_score_value = session.get('nhiss_score', 0)
    fullname = request.form["fullname"]
    age = request.form["age"]
    sex = request.form.get("sex")
    arrival = request.form["arrival"]
    systolic = request.form["systolic"]
    diastolic = request.form["diastolic"]
    heart_rate = request.form["heart-rate"]
    temperature = request.form["temp"]    
    oxygen_saturation = request.form["oxygen-saturation"]
    glucose = request.form["glucose"]
    current_medications = request.form["meds"]
    allergies = request.form["allergies"]
    stroke_history = request.form["previous-stroke-event"]
    medical_history = request.form.getlist("medical-history")
    radiologist_notes = request.form["radiologist-notes"]

    # ✅ Save uploaded CT image
    filename = None
    if 'CT-scan' in request.files:
        image = request.files['CT-scan']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

    # Format history
    if isinstance(medical_history, list):
        medical_history = ', '.join(medical_history)
    elif not medical_history:
        medical_history = 'No known Medical history'

    # Save to DB
    new_patient = Patient(
        fullname=fullname,
        age=age,
        sex=sex,
        arrival=arrival,
        systolic=systolic,
        diastolic=diastolic,
        heart_rate=heart_rate,
        temperature=temperature,
        oxygen_saturation=oxygen_saturation,
        glucose=glucose,
        current_medications=current_medications,
        allergies=allergies,
        stroke_history=stroke_history,
        medical_history=medical_history,
        radiologist_notes=radiologist_notes,
        nhiss_score=int(nhiss_score_value),
        ct_scan_filename=filename  # ✅ Save file to DB
    )
    db.session.add(new_patient)
    db.session.commit()

    return render_template("nhiss_score.html")

@app.route('/patient_case_review')
def patient_case_review():
    return render_template("patient_case_review.html")

@app.route('/patients_report')
def patients_report():
    patients = Patient.query.with_entities(Patient.age, Patient.nhiss_score).filter(
        Patient.nhiss_score.isnot(None), Patient.age.isnot(None)
    ).all()

  
    patient_data = [{"x": p.age, "y": p.nhiss_score} for p in patients]
    return render_template("patients_report.html",
                           total_patients=len(patients),
                           avg_time=32,  
                           discharges=68,  
                           patient_data=patient_data)


def upload():
    image = request.files['CT-scan']
    if image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(f"Image uploaded successfully: {filename}")
    else:
        print("no Image Selected")


@app.route('/patient_data_display')
def patient_data_display():
     return render_template('patient_data_display.html', **patient_data)

@app.route('/patient_list')

@app.route('/patient_list')
def patient_list():
    patients = Patient.query.order_by(Patient.id.desc()).all()
    return render_template('patient_list.html', patients=patients)


@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        new_user = UserAccount(
            username=request.form["username"],
            password=request.form["password"],
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
            email=request.form["email"],
            role=request.form["role"]
        )
        db.session.add(new_user)
        db.session.commit()
        return "Account request submitted. Approval may take 1–3 business days."
    return render_template("create_account.html")


@app.route('/patients/<int:patient_id>')
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template("view_patient.html", patient=patient)


from flask import flash

@app.route('/patients/<int:patient_id>/update', methods=["POST"])
def update_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    patient.diagnosis = request.form.get("diagnosis")
    patient.treatment = request.form.get("treatment")
    patient.neuro_approved = "neuro_approved" in request.form
    db.session.commit()
    flash("Patient case approved and notes submitted successfully.", "success")
    return redirect(url_for('neurologist_dashboard'))


@app.route('/schedule_appointment', methods=["GET", "POST"])
def schedule_appointment():
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        datetime = request.form.get("datetime")
        purpose = request.form.get("purpose")
        notes = request.form.get("notes")

        new_appointment = Appointment(
            patient_id=patient_id,
            datetime=datetime,
            purpose=purpose,
            notes=notes
        )

        db.session.add(new_appointment)
        db.session.commit()

        return redirect(url_for('neurologist_dashboard'))

    patients = Patient.query.all()
    return render_template("schedule_appointment.html", patients=patients)


if __name__ == "__main__":
    app.run(debug=True)

