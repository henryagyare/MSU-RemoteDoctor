from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

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
    

@app.route('/technician_dashboard')
def technician_dashboard():
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

@app.route('/confirm_page', methods=["POST"])
def confirm_page():
    # Patient Data from the Entry Form
    fullname = request.form["fullname"]
    age = request.form["age"]
    

    if request.method == 'POST':
        # return f"Fullname: {fullname},\t Age: {age}"
        return render_template("confirm_page.html")


if __name__ == "__main__":
    app.run(debug=True)