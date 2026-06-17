from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.models import Order, OrderItem, CartItem, Product

orders_bp = Blueprint("orders", __name__)


@orders_bp.post("/")
@jwt_required()
def place_order():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    shipping_address = data.get("shipping_address")
    if not shipping_address:
        return jsonify({"error": "shipping_address required"}), 400

    cart_items = CartItem.query.filter_by(user_id=user_id).all()
    if not cart_items:
        return jsonify({"error": "Cart is empty"}), 400

    total = 0
    order_items = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        if product.stock < item.quantity:
            return jsonify({"error": f"Insufficient stock for {product.name}"}), 400
        subtotal = product.price * item.quantity
        total += subtotal
        order_items.append(OrderItem(product_id=product.id, quantity=item.quantity, unit_price=product.price))
        product.stock -= item.quantity

    order = Order(user_id=user_id, total_amount=round(total, 2), shipping_address=shipping_address)
    db.session.add(order)
    db.session.flush()  # get order.id before commit

    for oi in order_items:
        oi.order_id = order.id
        db.session.add(oi)

    CartItem.query.filter_by(user_id=user_id).delete()
    db.session.commit()
    return jsonify({"message": "Order placed", "order_id": order.id, "total": order.total_amount}), 201


@orders_bp.get("/")
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    if claims.get("role") == "admin":
        orders = Order.query.order_by(Order.created_at.desc()).all()
    else:
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()

    return jsonify([_order_dict(o) for o in orders])


@orders_bp.get("/<int:order_id>")
@jwt_required()
def get_order(order_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    order = Order.query.get_or_404(order_id)
    if claims.get("role") != "admin" and order.user_id != user_id:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(_order_dict(order))


@orders_bp.put("/<int:order_id>/status")
@jwt_required()
def update_status(order_id):
    if get_jwt().get("role") != "admin":
        return jsonify({"error": "Admin only"}), 403
    order = Order.query.get_or_404(order_id)
    order.status = request.get_json().get("status", order.status)
    db.session.commit()
    return jsonify({"message": "Status updated", "status": order.status})


def _order_dict(order):
    return {
        "id": order.id,
        "status": order.status,
        "total_amount": order.total_amount,
        "shipping_address": order.shipping_address,
        "created_at": order.created_at.isoformat(),
        "items": [{
            "product_id": i.product_id,
            "name": i.product.name,
            "quantity": i.quantity,
            "unit_price": i.unit_price
        } for i in order.items]
    }
