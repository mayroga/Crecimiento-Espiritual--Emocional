from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
import openai
from langdetect import detect
from gtts import gTTS
import base64
from io import BytesIO
from flask_cors import CORS
import stripe

app = Flask(__name__)

# Permitir SOLO tu Google Site
CORS(app, origins=[
    "https://sites.google.com/view/felicidad",
    "https://sites.google.com/view/felicidad/*"
])

# =======================================================
# CONFIGURACIONES DE API
# =======================================================

USE_OPENAI = True

if USE_OPENAI:
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route("/")
def home():
    return render_template("index.html", stripe_pub_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

# =======================================================
# ENDPOINTS DE PAGO CON STRIPE
# =======================================================

@app.route("/create-donation-session", methods=["POST"])
def create_donation_session():
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
                    "product_data": {"name": "Donación a May Roga LLC"},
                    "unit_amount": amount_cents,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://sites.google.com/view/felicidad/página-principal?status=success",
            cancel_url="https://sites.google.com/view/felicidad/página-principal?status=cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/create-service-session", methods=["POST"])
def create_service_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": "Servicio de Crecimiento Emocional"},
                    "unit_amount": 1000,  # $10.00
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="https://sites.google.com/view/felicidad/página-principal?status=success",
            cancel_url="https://sites.google.com/view/felicidad/página-principal?status=cancel",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
