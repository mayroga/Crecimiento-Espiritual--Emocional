from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import openai
import google.generativeai as genai

app = Flask(__name__)

# =======================================================
# CORS: autorización específica para tu Google Site y APIs externas
# =======================================================
CORS(app, origins=[
    "https://sites.google.com/view/felicidad",  # tu Google Site exacto
    "https://checkout.stripe.com",              # Stripe Checkout
    "https://api.openai.com",                   # OpenAI
    "https://gemini.googleapis.com"             # Gemini
])

# =======================================================
# Configura Stripe (Render usa la clave secreta)
# =======================================================
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# =======================================================
# Rutas
# =======================================================
@app.route("/")
def index():
    # Le pasamos la clave pública al frontend (Google Site)
    return render_template("index.html", stripe_pub_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():
    try:
        data = request.get_json()
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": data.get("name", "Servicio de Bienestar")
                    },
                    "unit_amount": int(data.get("amount", 500)) * 100,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://sites.google.com/view/felicidad/success",
            cancel_url="https://sites.google.com/view/felicidad/cancel",
        )
        return jsonify({"id": session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# =======================================================
# Configura OpenAI y Gemini (sin cambiar nada de tu lógica)
# =======================================================
USE_OPENAI = True

if USE_OPENAI:
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

if __name__ == "__main__":
    app.run(port=5000)
