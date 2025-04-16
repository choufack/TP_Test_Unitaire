from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- MOCK DATA ---
menu = [
    {"id": 1, "name": "Burger", "price": 5.0, "customizations": ["Cheese", "Bacon"]},
    {"id": 2, "name": "Fries", "price": 2.5, "customizations": []},
]
orders = []
order_status = ["Préparation", "Prête", "Livrée"]
cart = {
    "items": [],
    "total": 0.0
}

# ========== MENU MANAGEMENT ==========

@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(menu)

@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    if not data or "name" not in data or "price" not in data:
        return jsonify({"message": "Invalid menu item data"}), 400
    new_item = {
        "id": len(menu) + 1,
        "name": data["name"],
        "price": data["price"],
        "customizations": data.get("customizations", [])
    }
    menu.append(new_item)
    return jsonify({"message": "Item added", "menu": menu}), 201

@app.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    item = next((item for item in menu if item["id"] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    item["name"] = data.get("name", item["name"])
    item["price"] = data.get("price", item["price"])
    item["customizations"] = data.get("customizations", item["customizations"])
    return jsonify({"message": "Item updated", "item": item}), 200

@app.route('/menu/<int:item_id>', methods=['DELETE'])
def delete_menu_item(item_id):
    global menu
    item = next((item for item in menu if item["id"] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    menu = [item for item in menu if item["id"] != item_id]
    return jsonify({"message": "Item deleted", "menu": menu}), 200

# ========== PANIER / CART ==========

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.json
    item_id = data.get("id")
    item = next((item for item in menu if item["id"] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404
    cart["items"].append(item)
    cart["total"] += item["price"]
    return jsonify({"message": "Item added to cart", "cart": cart}), 200

@app.route('/cart/clear', methods=['POST'])
def clear_cart():
    cart["items"].clear()
    cart["total"] = 0.0
    return jsonify({"message": "Cart cleared"}), 200

@app.route('/cart', methods=['GET'])
def get_cart():
    return jsonify(cart)

# ========== COMMANDES ==========

@app.route('/order', methods=['POST'])
def create_order():
    if not cart["items"]:
        return jsonify({"message": "Cart is empty"}), 400
    new_order = {
        "id": len(orders) + 1,
        "items": cart["items"].copy(),
        "total": cart["total"],
        "status": "Préparation",
        "paid": False
    }
    orders.append(new_order)
    cart["items"].clear()
    cart["total"] = 0.0
    return jsonify({"message": "Order created", "order": new_order}), 201

@app.route('/order/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get("status")
    if new_status not in order_status:
        return jsonify({"message": "Invalid status"}), 400
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    order["status"] = new_status
    return jsonify({"message": "Order status updated", "order": order}), 200

@app.route('/order/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order["paid"]:
        return jsonify({"message": "Order already paid"}), 400
    order["paid"] = True
    return jsonify({"message": "Payment successful", "order": order}), 200

@app.route('/order/<int:order_id>/cancel', methods=['POST'])
def cancel_order(order_id):
    global orders
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    if order["status"] != "Préparation":
        return jsonify({"message": "Order cannot be canceled. It is already finalized."}), 400
    orders = [o for o in orders if o["id"] != order_id]
    return jsonify({"message": "Order canceled successfully"}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    return jsonify(orders)

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({"order": order})

# ========== TEMPLATES ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu-page')
def menu_page():
    return render_template('menu.html')

@app.route('/cart-page')
def cart_page():
    return render_template('cart.html')

@app.route('/orders-page')
def orders_page():
    return render_template('orders.html')

# ========== LANCEMENT ==========

if __name__ == '__main__':
    app.run(debug=True)
