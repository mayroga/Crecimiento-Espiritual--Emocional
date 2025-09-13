from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import stripe
import os
import google.generativeai as genai
from gtts import gTTS
from langdetect import detect
import tempfile

app = Flask(__name__)
CORS(app)

# Configuración Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_REEMPLAZA_CON_TU_KEY")
PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "pk_live_51NqPxQBOA5mT4t0PEoRVRc0Sj7DugiHvxhozC3BYh0q0hAx1N3HCLJe4xEp3MSuNMA6mQ7fAO4mvtppqLodrtqEn00pgJNQaxz")

# Configuración Google Generative AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", "AIzaSyDUMMY-KEY"))

# Página principal
@app.route("/")
def index():
    return render_template("index.html", key=PUBLISHABLE_KEY)

# Endpoint Stripe: Donaciones con validación
@app.route("/create-donation-session", methods=["POST"])
def create_donation_session():
    try:
        data = request.json
        amount = int(float(data.get("amount", 0)) * 100)  # convertir a centavos USD
        if amount < 50:  # mínimo $0.50
            amount = 50

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Donación abierta'},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            success_url="https://tu-dominio.com/success",
            cancel_url="https://tu-dominio.com/cancel",
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Endpoint Stripe: Pago de servicio con validación
@app.route("/create-service-session", methods=["POST"])
def create_service_session():
    try:
        data = request.json
        amount = int(float(data.get("amount", 0)) * 100)  # centavos USD
        if amount < 100:  # mínimo $1
            amount = 100

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            mode='payment',
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': 'Servicio de Risoterapia'},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            success_url="https://tu-dominio.com/success",
            cancel_url="https://tu-dominio.com/cancel",
        )
        return jsonify({'id': session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

# Endpoint Chat IA + TTS
@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        message = data.get("message", "")

        # IA: no juzgar, no discutir, solo guiar al bien o evitar lo dañino inteligentemente
        prompt = f"""
        Actúa como un asistente de risoterapia y bienestar natural.
        - Nunca juzgues ni discutas con el cliente.
        - Si el tema es negativo, conviértelo en un debate hacia el bien.
        - Si es algo prohibido o dañino, evítalo inteligentemente, sin que sea notado.
        - Siempre responde de forma breve, clara y positiva.
        Usuario: {message}
        """

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        reply = response.text.strip()

        # Detectar idioma
        lang = "es"
        try:
            lang = detect(reply)
        except:
            pass

        # Generar TTS
        tts = gTTS(reply, lang=lang)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)

        return jsonify({"reply": reply, "audio": temp_file.name})
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
