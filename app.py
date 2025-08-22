from flask import Flask, render_template, request, redirect, url_for, send_file, flash, session
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages

# Configure upload folder
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Simulated storage for extracted results (replace with database later)
extracted_results = {}

USERS = {
    "venn": "venn",
    "pedro": "pedro"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in USERS and USERS[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return render_template("dashboard.html")


@app.route("/main")
def main():
    if "user" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    return render_template("main.html")

@app.route("/process", methods=["POST"])
def process():
    if "pdf_file" not in request.files:
        return render_template("main.html", error="No file uploaded")

    file = request.files["pdf_file"]
    if file.filename == "":
        return render_template("main.html", error="No file selected")

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    # --- AI extraction placeholder logic ---
    # Replace this with your real extraction pipeline
    specs_id = filename  # could be UUID
    extracted_specs = {
        "id": specs_id,
        "endpoints": ["Primary endpoint: Survival rate", "Secondary endpoint: Adverse events"],
        "eligibility": ["Adults 18-65", "No prior chemotherapy"],
        "parameters": ["Sample size: 200", "Randomized, double-blind"]
    }
    extracted_results[specs_id] = extracted_specs

    return render_template("main.html", specs=extracted_specs)

@app.route("/download/<specs_id>")
def download(specs_id):
    if specs_id not in extracted_results:
        flash("Specification not found.")
        return redirect(url_for("main"))

    # For now, just dump results to a text file
    specs = extracted_results[specs_id]
    output_file = os.path.join(app.config["UPLOAD_FOLDER"], f"{specs_id}_specs.txt")

    with open(output_file, "w") as f:
        f.write("Draft Study Specifications\n")
        f.write("="*30 + "\n\n")
        f.write("Endpoints:\n")
        for ep in specs["endpoints"]:
            f.write(f"- {ep}\n")
        f.write("\nEligibility Criteria:\n")
        for el in specs["eligibility"]:
            f.write(f"- {el}\n")
        f.write("\nStudy Parameters:\n")
        for param in specs["parameters"]:
            f.write(f"- {param}\n")

    return send_file(output_file, as_attachment=True)

@app.route("/logout")
def logout():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()