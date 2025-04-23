from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        return redirect(url_for("technician_dashboard"))
        pass # verify user data and proceded
    

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


if __name__ == "__main__":
    app.run(debug=True)