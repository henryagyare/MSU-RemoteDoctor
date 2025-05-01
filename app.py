from flask import Flask, render_template, request, redirect, url_for, jsonify 
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy 
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
    status = db.Column(db.String(10), default='pending')  # pending, approved, denied

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
    radiologist_notes =db.Column(db.String(500))
    # nhiss_score = db.Column(db.Integer)
    # neuro_approved = db.Column(db.Integer)

with app.app_context():
    db.create_all()

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


@app.route('/technician_dashboard', methods=["POST", "GET"])
def technician_dashboard():
    if request.method == "POST":
        search_item = request.form["search_patients"]
        return f"You searched for {search_item}" # Re-render the technician dashboard page and let the displayed items be the search result.
    return render_template('technician_dashboard.html')

@app.route('/neurologist_dashboard')
def neurologist_dashboard():
    return render_template('neurologist_dashboard.html')
    
@app.route('/patient_data_entry')
def patient_data_entry():
    return render_template("patient_data_entry.html")

@app.route('/nhiss_score', methods = ["POST"])
def nhiss_score():
    # Patient Data from the Entry Form
    fullname = request.form["fullname"]
    age = request.form["age"]
    sex =  request.form.get("sex")
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
    

    upload()

    if isinstance(medical_history, list):
        medical_history = ', '.join(medical_history)

    elif not medical_history:
        medical_history = 'No known Medical history'

    if request.method == 'POST':
        new_patient = Patient(fullname = fullname, age = age, sex = sex, arrival = arrival , 
                          systolic = systolic, diastolic = diastolic, heart_rate = heart_rate, 
                          temperature = temperature, oxygen_saturation = oxygen_saturation, glucose = glucose,
                          current_medications = current_medications, allergies = allergies,stroke_history =stroke_history, 
                          medical_history = medical_history, radiologist_notes = radiologist_notes)
        db.session.add(new_patient)       
        db.session.commit() 

    return render_template("nhiss_score.html")

@app.route('/patient_case_review')
def patient_case_review():
    return render_template("patient_case_review.html")

@app.route('/patients_report')
def patients_report():
    return render_template("patients_report.html")

def upload():
    image = request.files['CT-scan']
    if image.filename != '':
        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        print(f"Image uploaded successfully: {filename}")
    else:
        print("no Image Selected")

@app.route('/confirm_page', methods=["POST"])
def confirm_page():
    if request.method == 'POST':
        global nhiss_score_calculated
        nhiss_score_calculated = request.form["nhiss_score"]
        return render_template("confirm_page.html")

@app.route("/search_patients", methods=["POST"])
def search_patients():
    result = []

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        patient_id = request.form.get('patient_id', '').strip()

        query = Patient.query 

        if name:
             query = query.filter(Patient.fullname.ilike(f'%{name}%'))
        if patient_id:
            query = query.filter(Patient.id == patient_id)

        if not name and not patient_id:
            query = query.order_by(Patient.arrival.desc()).limit(8)

        results = query.order_by(Patient.arrival.desc()).limit(8).all()

        return jsonify([
        {
            'id': p.id,
            'fullname': p.fullname,
            'arrival': p.arrival.strftime('%Y-%m-%d %H:%M')
        } for p in results
        ])

@app.route('/patient_data_display')
def patient_data_display():
     return render_template('patient_data_display.html', **patient_data)

@app.route('/patient_list')
def patient_list():
    patients = patient_data_list
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


if __name__ == "__main__":
    app.run(debug=True)

