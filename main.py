from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import google.generativeai as genai
from gtts import gTTS
from langdetect import detect
import os
import time

app = Flask(__name__)
CORS(app)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Guardar tiempo de inicio de sesión
session_start = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_id = request.remote_addr  # identificar al usuario por IP
    now = time.time()

    # Revisar si la sesión está activa
    if user_id in session_start:
        elapsed = now - session_start[user_id]
        if elapsed > 180:  # 3 minutos = 180 segundos
            session_start.pop(user_id, None)
            return jsonify({
                "response": "Tu sesión de 3 minutos ha terminado. Si deseas continuar, por favor comienza una nueva."
            })

    else:
        # iniciar nueva sesión
        session_start[user_id] = now

    data = request.json
    prompt = data.get("prompt", "")

    # Limitar tema a religión y espiritualidad
    if not any(word in prompt.lower() for word in ["dios", "biblia", "espiritual", "religión", "fe", "iglesia", "oración", "alma"]):
        return jsonify({
            "response": "Este servicio está dedicado exclusivamente a temas de religión y crecimiento espiritual-emocional. Por favor, formula tu pregunta dentro de ese contexto."
        })

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/donate", methods=["POST"])
def donate():
    try:
        data = request.json
        amount = int(float(data["amount"]) * 100)  # convertir a centavos
        if amount < 100:  # mínimo $1
            return jsonify({"error": "El monto mínimo de donación es $1 USD."}), 400

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Donación para el servicio de Crecimiento Espiritual-Emocional",
                        "description": "Tu aporte se usará para apoyar al dueño y sus trabajadores, arreglos y actualizaciones del servicio, ayudar a personas necesitadas, comprar alimentos, ropa, zapatos y shelter."
                    },
                    "unit_amount": amount,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=request.host_url,
            cancel_url=request.host_url,
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
