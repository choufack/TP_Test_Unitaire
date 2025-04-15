from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask import render_template

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Mock data
menu = [
    {"id": 1, "name": "Burger", "price": 5.0, "customizations": ["Cheese", "Bacon"]},
    {"id": 2, "name": "Fries", "price": 2.5, "customizations": []},
]
orders = []
order_status = ["Preparation", "Ready", "Delivered"]
cart = {
    "items": [],
    "total": 0.0
}

# Routes for menu management
@app.route('/menu', methods=['GET'])
def get_menu():
    return jsonify(menu)

@app.route('/menu', methods=['POST'])
def add_menu_item():
    data = request.json
    if not data or "name" not in data or "price" not in data:
        return jsonify({"message": "Invalid menu item data"}), 400

    new_item = {
        "id": len(menu) + 1,  # Générer un ID unique
        "name": data["name"],
        "price": data["price"],
        "customizations": data.get("customizations", [])  # Optionnel
    }
    menu.append(new_item)
    return jsonify({"message": "Item added", "menu": menu}), 201

@app.route('/menu/<int:item_id>', methods=['PUT'])
def update_menu_item(item_id):
    data = request.json
    item = next((item for item in menu if item["id"] == item_id), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    # Mettre à jour les champs de l'article
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

# Routes for cart management
@app.route('/cart', methods=['POST'])
def add_to_cart():
    data = request.json
    if not data or "id" not in data:
        return jsonify({"message": "Invalid item data"}), 400

    # Trouver l'article dans le menu
    item = next((item for item in menu if item["id"] == data["id"]), None)
    if not item:
        return jsonify({"message": "Item not found"}), 404

    # Ajouter l'article au panier
    cart["items"].append(item)
    cart["total"] += item["price"]

    # Appliquer les promotions
    apply_promotions(cart)

    return jsonify({"message": "Item added to cart", "cart": cart}), 200

@app.route('/cart', methods=['GET'])
def get_cart():
    apply_promotions(cart)
    return jsonify(cart)

@app.route('/cart', methods=['DELETE'])
def clear_cart():
    global cart
    cart = {
        "items": [],
        "total": 0.0
    }
    return jsonify({"message": "Cart cleared", "cart": cart}), 200

# Promotion management
def apply_promotions(cart):
    # Exemple de promotion : 10% de réduction si le total dépasse 20
    if cart["total"] > 20:
        discount = cart["total"] * 0.1
        cart["discount"] = round(discount, 2)
        cart["final_total"] = round(cart["total"] - discount, 2)
    else:
        cart["discount"] = 0.0
        cart["final_total"] = cart["total"]

# Routes for order management
@app.route('/order', methods=['POST'])
def create_order():
    global cart, orders

    # Vérifier si le panier est vide
    if not cart["items"]:
        return jsonify({"message": "Cart is empty. Cannot create an order."}), 400

    # Générer un ID unique pour la commande
    order_id = len(orders) + 1

    # Créer une commande
    order = {
        "id": order_id,
        "items": cart["items"],
        "total": cart["total"],
        "discount": cart.get("discount", 0.0),
        "final_total": cart.get("final_total", cart["total"]),
        "status": "Preparation"  # Statut initial de la commande
    }

    # Ajouter la commande à la liste des commandes
    orders.append(order)

    # Vider le panier
    cart = {
        "items": [],
        "total": 0.0,
        "discount": 0.0,
        "final_total": 0.0
    }

    return jsonify({"message": "Order created", "order": order}), 201

# Routes for order status management (payment)
app.route('/order/<int:order_id>/pay', methods=['POST'])
def pay_order(order_id):
    global orders
    # Trouver la commande par son ID
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # Vérifier si la commande est encore en préparation
    if order["status"] != "Preparation":
        return jsonify({"message": "Order cannot be paid. It is already finalized."}), 400

    # Simuler le paiement
    order["status"] = "Paid"

    return jsonify({"message": "Order paid successfully", "order": order}), 200

# Routes for order status management (update and cancel)
@app.route('/order/<int:order_id>', methods=['DELETE'])
def cancel_order(order_id):
    global orders
    # Trouver la commande par son ID
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    # Vérifier si la commande est encore en préparation
    if order["status"] != "Preparation":
        return jsonify({"message": "Order cannot be canceled. It is already finalized."}), 400

    # Supprimer la commande
    orders = [order for order in orders if order["id"] != order_id]
    return jsonify({"message": "Order canceled successfully"}), 200

@app.route('/orders', methods=['GET'])
def get_orders():
    print("Current orders:", orders)
    return jsonify(orders)

@app.route('/order/<int:order_id>', methods=['GET'])
def get_order_status(order_id):
    order = next((order for order in orders if order["id"] == order_id), None)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    return jsonify({"order": order})

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/menu')
def menu_page():
    return render_template('menu.html')

@app.route('/cart')
def cart_page():
    return render_template('cart.html')

@app.route('/orders')
def orders_page():
    return render_template('orders.html')