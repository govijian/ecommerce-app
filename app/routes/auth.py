from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db, bcrypt
from app.models.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    data = request.get_json()
    if not data or not all(k in data for k in ("email", "password", "name")):
        return jsonify({"error": "email, password, name required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        email=data["email"],
        name=data["name"],
        password_hash=bcrypt.generate_password_hash(data["password"]).decode("utf-8"),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "User registered", "id": user.id}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data.get("email")).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, data.get("password", "")):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"access_token": token, "role": user.role, "name": user.name})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"id": user.id, "email": user.email, "name": user.name, "role": user.role})
