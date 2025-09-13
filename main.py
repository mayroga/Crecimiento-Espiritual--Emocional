from flask import Flask, render_template, request, jsonify
import os
from flask_cors import CORS
import stripe

app = Flask(__name__)

# 🔒 Permitir SOLO tu Google Site
CORS(app, origins=[
    "https://sites.google.com/view/felicidad",
    "https://sites.google.com/view/felicidad/*"
])

# 🔑 Configuración de Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route("/")
def home():
    return render_template("index.html", stripe_pub_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

# 💳 Endpoint único para donación/pago
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.json
        amount = float(data.get("amount", 0))
        if amount < 4.99:
            return jsonify({"error": "La donación mínima es $4.99"}), 400

        amount_cents = int(amount * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Aporte a May Roga LLC"},
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            # 🔁 Siempre vuelve a tu Google Site
            success_url="https://sites.google.com/view/felicidad/?status=success",
            cancel_url="https://sites.google.com/view/felicidad/?status=cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
