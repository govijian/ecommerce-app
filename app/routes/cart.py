from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.models import CartItem, Product

cart_bp = Blueprint("cart", __name__)


@cart_bp.get("/")
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    result = []
    for item in items:
        p = item.product
        result.append({
            "cart_item_id": item.id,
            "product_id": p.id,
            "name": p.name,
            "price": p.price,
            "quantity": item.quantity,
            "subtotal": round(p.price * item.quantity, 2)
        })
    total = round(sum(i["subtotal"] for i in result), 2)
    return jsonify({"items": result, "total": total})


@cart_bp.post("/")
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get_or_404(product_id)
    if product.stock < quantity:
        return jsonify({"error": "Insufficient stock"}), 400

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        db.session.add(CartItem(user_id=user_id, product_id=product_id, quantity=quantity))
    db.session.commit()
    return jsonify({"message": "Added to cart"}), 201


@cart_bp.put("/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    quantity = request.get_json().get("quantity", 1)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Cart updated"})


@cart_bp.delete("/<int:item_id>")
@jwt_required()
def remove_from_cart(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed"})


@cart_bp.delete("/")
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared"})
