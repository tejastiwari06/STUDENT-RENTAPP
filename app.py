import os
import re
import uuid
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, session
)
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

# ── Firebase ─────────────────────────────────────────────────
try:
    from firebase_config import init_firebase, get_db_ref
    init_firebase()
    USE_FIREBASE = True
except FileNotFoundError as e:
    print(f"\n⚠️  Firebase not configured: {e}")
    print("   Running in DEMO mode — data stored in memory only.\n")
    USE_FIREBASE = False
except Exception as e:
    print(f"\n⚠️  Firebase init error: {e}")
    print("   Running in DEMO mode — data stored in memory only.\n")
    USE_FIREBASE = False

# ── App Config ───────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

UPLOAD_FOLDER = os.path.join("static", "uploads")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ── In-memory fallback stores ─────────────────────────────────
_memory_requests: dict = {}
_memory_users: dict = {}


# ── Auth Helpers ─────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)
    return decorated


def get_user(username: str) -> dict | None:
    if USE_FIREBASE:
        return get_db_ref(f"/users/{username}").get()
    return _memory_users.get(username)


def create_user(username: str, email: str, password: str) -> bool:
    """Returns False if username already exists."""
    if get_user(username):
        return False
    user = {
        "username": username,
        "email":    email,
        "password": generate_password_hash(password),
        "created_at": datetime.now().strftime("%d %b %Y, %H:%M"),
    }
    if USE_FIREBASE:
        get_db_ref(f"/users/{username}").set(user)
    else:
        _memory_users[username] = user
    return True


def verify_user(username: str, password: str) -> dict | None:
    """Returns user dict on success, None on failure."""
    user = get_user(username)
    if user and check_password_hash(user["password"], password):
        return user
    return None


# ── Request Helpers ───────────────────────────────────────────
def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_phone(phone: str) -> bool:
    return bool(re.fullmatch(r"[0-9]{7,15}", phone.strip()))


def save_request(data: dict) -> str:
    req_id = str(uuid.uuid4())[:8]
    data["id"] = req_id
    data["status"] = "pending"
    data["screenshot"] = ""
    data["created_at"] = datetime.now().strftime("%d %b %Y, %H:%M")
    data["posted_by"] = session.get("user", "unknown")

    if USE_FIREBASE:
        get_db_ref(f"/requests/{req_id}").set(data)
    else:
        _memory_requests[req_id] = data
    return req_id


def get_all_requests() -> list:
    if USE_FIREBASE:
        snapshot = get_db_ref("/requests").get()
        if not snapshot:
            return []
        items = list(snapshot.values())
    else:
        items = list(_memory_requests.values())

    items.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return items


def get_request(req_id: str) -> dict | None:
    if USE_FIREBASE:
        return get_db_ref(f"/requests/{req_id}").get()
    return _memory_requests.get(req_id)


def update_request(req_id: str, updates: dict) -> None:
    if USE_FIREBASE:
        get_db_ref(f"/requests/{req_id}").update(updates)
    else:
        if req_id in _memory_requests:
            _memory_requests[req_id].update(updates)


# ── Auth Routes ───────────────────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        errors = []

        if not username or len(username) < 3:
            errors.append("Username must be at least 3 characters.")
        if not re.fullmatch(r"[a-z0-9_]{3,20}", username):
            errors.append("Username may only contain letters, numbers, and underscores (3–20 chars).")
        if not email or "@" not in email:
            errors.append("A valid email address is required.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")

        if not errors:
            if create_user(username, email, password):
                session["user"] = username
                session["email"] = email
                flash(f"Welcome aboard, {username}! 🎉 Your account is ready.", "success")
                return redirect(url_for("index"))
            else:
                errors.append("That username is already taken. Please choose another.")

        return render_template("register.html", errors=errors, form_data=request.form)

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("index"))

    next_url = request.args.get("next", "")

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")
        next_url = request.form.get("next_url", "")

        errors = []

        if not username:
            errors.append("Username is required.")
        if not password:
            errors.append("Password is required.")

        if not errors:
            user = verify_user(username, password)
            if user:
                session["user"]  = user["username"]
                session["email"] = user.get("email", "")
                flash(f"Welcome back, {user['username']}! 👋", "success")
                return redirect(next_url or url_for("index"))
            else:
                errors.append("Incorrect username or password.")

        return render_template("login.html", errors=errors, form_data=request.form, next_url=next_url)

    return render_template("login.html", next_url=next_url)


@app.route("/logout")
def logout():
    username = session.pop("user", None)
    session.pop("email", None)
    if username:
        flash(f"You've been logged out. See you soon, {username}!", "success")
    return redirect(url_for("login"))


# ── App Routes (protected) ────────────────────────────────────

@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
@login_required
def submit():
    name     = request.form.get("name", "").strip()
    phone    = request.form.get("phone", "").strip()
    location = request.form.get("location", "").strip()
    time_val = request.form.get("time", "").strip()
    purpose  = request.form.get("purpose", "").strip()
    cost     = request.form.get("cost", "").strip()

    errors = []

    if not name:
        errors.append("Full name is required.")
    if not phone:
        errors.append("Phone number is required.")
    elif not validate_phone(phone):
        errors.append("Phone must contain digits only and be 7–15 characters long.")
    if not location:
        errors.append("Location is required.")
    if not time_val:
        errors.append("Time / duration is required.")
    if not purpose:
        errors.append("Purpose / description is required.")
    if not cost:
        errors.append("Cost is required.")
    else:
        try:
            if float(cost) < 0:
                errors.append("Cost must be a positive number.")
        except ValueError:
            errors.append("Cost must be a valid number.")

    if errors:
        return render_template("index.html", errors=errors, form_data=request.form)

    save_request({
        "name": name, "phone": phone, "location": location,
        "time": time_val, "purpose": purpose, "cost": cost,
    })
    flash("Your rental request has been posted successfully! 🎉", "success")
    return redirect(url_for("dashboard"))


@app.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    return render_template("dashboard.html", requests=get_all_requests())


@app.route("/action/<req_id>", methods=["POST"])
@login_required
def action(req_id: str):
    action_val = request.form.get("action", "").lower()

    if action_val not in ("accept", "reject"):
        flash("Invalid action.", "error")
        return redirect(url_for("dashboard"))

    req = get_request(req_id)
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for("dashboard"))

    if req.get("status") != "pending":
        flash("This request has already been processed.", "error")
        return redirect(url_for("dashboard"))

    update_request(req_id, {"status": action_val + "ed"})

    if action_val == "accept":
        flash("Request accepted! Please upload a booking screenshot.", "success")
        return redirect(url_for("confirm", req_id=req_id))
    else:
        flash("Request has been rejected.", "success")
        return redirect(url_for("dashboard"))


@app.route("/confirm/<req_id>", methods=["GET"])
@login_required
def confirm(req_id: str):
    req = get_request(req_id)
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for("dashboard"))
    return render_template("confirmation.html", request_data=req)


@app.route("/upload/<req_id>", methods=["POST"])
@login_required
def upload(req_id: str):
    req = get_request(req_id)
    if not req:
        flash("Request not found.", "error")
        return redirect(url_for("dashboard"))

    if "screenshot" not in request.files or request.files["screenshot"].filename == "":
        return render_template("confirmation.html", request_data=req, errors=["No file selected."])

    file = request.files["screenshot"]
    if not allowed_file(file.filename):
        return render_template("confirmation.html", request_data=req, errors=["Only JPG and PNG files are allowed."])

    filename = secure_filename(f"{req_id}_{uuid.uuid4().hex[:6]}_{file.filename}")
    file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    update_request(req_id, {"screenshot": filename})

    flash("Booking screenshot uploaded! ✅ Your booking is confirmed.", "success")
    return redirect(url_for("dashboard"))


# ── API ───────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "firebase": USE_FIREBASE})


# ── Error Handlers ────────────────────────────────────────────
@app.errorhandler(413)
def request_too_large(e):
    flash("File too large. Maximum size is 5 MB.", "error")
    return redirect(request.referrer or url_for("dashboard"))


@app.errorhandler(404)
def not_found(e):
    return redirect(url_for("login"))


# ── Entry Point ───────────────────────────────────────────────
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")
    port  = int(os.getenv("PORT", 5000))
    print(f"\n🚀 Hanashi Kikuyo running → http://localhost:{port}")
    print(f"   Firebase: {'✅ connected' if USE_FIREBASE else '⚠️  demo mode (no Firebase)'}\n")
    app.run(debug=debug, host="0.0.0.0", port=port)
