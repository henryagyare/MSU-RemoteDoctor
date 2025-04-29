from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

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
    if request.method == "POST":            
        patient_data["fullname"] = request.form["fullname"]
        patient_data["age"] = request.form["age"]
        patient_data["sex"] =  request.form.get("sex")
        patient_data["arrival"] = request.form["arrival"]
        patient_data["systolic"] = request.form["systolic"]
        patient_data["diastolic"] = request.form["diastolic"]
        patient_data["heart_rate"] = request.form["heart-rate"]
        patient_data["temperature"] = request.form["temp"]    
        patient_data["oxygen_saturation"] = request.form["oxygen-saturation"]
        patient_data["glucose"] = request.form["glucose"]
        patient_data["current_medications"] = request.form["meds"]
        patient_data["allergies"] = request.form["allergies"]
        patient_data["stroke_history"] = request.form["previous-stroke-event"]
        patient_data["medical_history"] = request.form.getlist("medical-history")
        patient_data["radiologist_notes"] = request.form["radiologist-notes"]

        patient_data_list.append(patient_data)

        upload()

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
        nhiss_score = request.form["nhiss_score"]
        return render_template("confirm_page.html")

@app.route("/search_patients", methods=["POST"])
def search_patients():
    search_item = request.form["search_patients"]
    return f"You searched for {search_item}"

@app.route('/patient_data_display')
def patient_data_display():
     return render_template('patient_data_display.html', **patient_data)

@app.route('/patient_list')
def patient_list():
    patients = patient_data_list
    print("Patients: ", patients)
    return render_template('patient_list.html', patients=patients)
    # return patients


if __name__ == "__main__":
    app.run(debug=True)

