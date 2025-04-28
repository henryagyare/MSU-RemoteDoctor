from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return redirect(url_for("login"))

#created a dummy 2d-dictionary of technician and neurologist login information. Data will be later from data base
users = {
        'HenryAsante' : {'password' : 'nurse1223', 'role': 'technician'},
        'ChrisGadze' : {'password' : 'neuro2234', 'role' : 'neurologist'}
        }

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")  # show form on GET

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role').lower()  # normalize role

        # Dummy users dictionary for demonstration. Users credentials will be later sourced from the database
        users = {
            'HenryAsante': {'password': 'nurse1234', 'role': 'technician'},
            'ChrisGadze': {'password': 'neuro2234', 'role': 'neurologist'}
        }

        user = users.get(username)


        if user and user['password'] == password and user['role'] == role:
            if role == 'technician':
                return redirect(url_for('technician_dashboard'))
            elif role == 'neurologist':
                return redirect(url_for('neurologist_dashboard'))
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

@app.route("/neurologist")
def neurologist():
    pass
    
@app.route('/patient_data_entry')
def patient_data_entry():

    return render_template("patient_data_entry.html")

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

    if request.method == 'POST':
        # return f"Fullname: {fullname},\t Age: {age}"
        return render_template("confirm_page.html")

@app.route("/search_patients", methods=["POST"])
def search_patients():
    search_item = request.form["search_patients"]
    return f"You searched for {search_item}"


@app.route('/nhiss_score')
def nhiss_score():
    return render_template('nhiss_score.html')

if __name__ == "__main__":
    app.run(debug=True)