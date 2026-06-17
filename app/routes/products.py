from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app import db
from app.models.models import Product

products_bp = Blueprint("products", __name__)


def admin_required():
    claims = get_jwt()
    return claims.get("role") == "admin"


@products_bp.get("/")
def list_products():
    category = request.args.get("category")
    query = Product.query
    if category:
        query = query.filter_by(category=category)
    products = query.all()
    return jsonify([{
        "id": p.id, "name": p.name, "description": p.description,
        "price": p.price, "stock": p.stock, "category": p.category,
        "image_url": p.image_url
    } for p in products])


@products_bp.get("/<int:product_id>")
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify({
        "id": p.id, "name": p.name, "description": p.description,
        "price": p.price, "stock": p.stock, "category": p.category,
        "image_url": p.image_url
    })


@products_bp.post("/")
@jwt_required()
def create_product():
    if not admin_required():
        return jsonify({"error": "Admin only"}), 403
    data = request.get_json()
    p = Product(
        name=data["name"], description=data.get("description"),
        price=data["price"], stock=data.get("stock", 0),
        category=data.get("category"), image_url=data.get("image_url")
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({"id": p.id, "message": "Product created"}), 201


@products_bp.put("/<int:product_id>")
@jwt_required()
def update_product(product_id):
    if not admin_required():
        return jsonify({"error": "Admin only"}), 403
    p = Product.query.get_or_404(product_id)
    data = request.get_json()
    for field in ("name", "description", "price", "stock", "category", "image_url"):
        if field in data:
            setattr(p, field, data[field])
    db.session.commit()
    return jsonify({"message": "Product updated"})


@products_bp.delete("/<int:product_id>")
@jwt_required()
def delete_product(product_id):
    if not admin_required():
        return jsonify({"error": "Admin only"}), 403
    p = Product.query.get_or_404(product_id)
    db.session.delete(p)
    db.session.commit()
    return jsonify({"message": "Product deleted"})
