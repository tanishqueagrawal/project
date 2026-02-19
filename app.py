from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required
)
import bcrypt
import os

app = Flask(__name__)

# Config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["JWT_SECRET_KEY"] = "secretkey"
app.config["UPLOAD_FOLDER"] = "uploads"

CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)

# Create upload folder
if not os.path.exists("uploads"):
    os.makedirs("uploads")

# -------------------------
# Database Models
# -------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200))
    user_id = db.Column(db.Integer)

# Create database
with app.app_context():
    db.create_all()

# -------------------------
# Register API
# -------------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.json

    hashed = bcrypt.hashpw(
        data["password"].encode("utf-8"),
        bcrypt.gensalt()
    )

    user = User(
        email=data["email"],
        password=hashed.decode("utf-8")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})

# -------------------------
# Login API
# -------------------------

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({"error": "User not found"}), 401

    if bcrypt.checkpw(
        data["password"].encode("utf-8"),
        user.password.encode("utf-8")
    ):
        token = create_access_token(identity=user.id)
        return jsonify({"token": token})

    return jsonify({"error": "Wrong password"}), 401

# -------------------------
# Upload Image/PDF
# -------------------------

@app.route("/upload", methods=["POST"])
@jwt_required()
def upload_file():

    if "file" not in request.files:
        return jsonify({"error": "No file"}), 400

    file = request.files["file"]

    # Allow only images and PDFs
    if not (
        file.filename.endswith(".png") or
        file.filename.endswith(".jpg") or
        file.filename.endswith(".jpeg") or
        file.filename.endswith(".pdf")
    ):
        return jsonify({"error": "Only images and PDFs allowed"}), 400

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    new_file = File(filename=file.filename)
    db.session.add(new_file)
    db.session.commit()

    return jsonify({"message": "File uploaded"})

# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
