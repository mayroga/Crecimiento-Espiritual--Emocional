from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from langdetect import detect
from gtts import gTTS
import base64
from io import BytesIO
from flask_cors import CORS
import stripe

app = Flask(__name__)
CORS(app)

# Configura Gemini / Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configura Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")  # Tu secret key en variables de entorno

@app.route("/")
def home():
    return render_template("index.html", title="Crecimiento Espiritual-Emocional", stripe_pub_key=os.getenv("STRIPE_PUBLISHABLE_KEY"))

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"reply": "Por favor escribe algo.", "audio": ""})

    try:
        idioma = detect(user_msg)
    except:
        idioma = "es"

    lower_msg = user_msg.lower()
    if any(x in lower_msg for x in ["cristiano", "iglesia", "jesús"]):
        religion = "cristianismo"
    elif any(x in lower_msg for x in ["musulmán", "islam", "mezquita"]):
        religion = "islam"
    elif any(x in lower_msg for x in ["budista", "buda", "templo"]):
        religion = "budismo"
    elif any(x in lower_msg for x in ["judío", "sinagoga", "judaísmo"]):
        religion = "judaísmo"
    else:
        religion = "universal"

    # Genera respuesta
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Saluda primero al usuario, pregunta cómo lo puedes ayudar hoy, y actúa como guía espiritual {religion}. Responde en {idioma}. Usuario dice: {user_msg}"
        response = model.generate_content(prompt)
        reply_text = response.text
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        reply_text = "Lo siento, hubo un problema al generar la respuesta. Por favor, inténtalo de nuevo más tarde."

    # Convertir a audio
    tts_lang = idioma[:2] if idioma[:2] in ["es","en","fr","de","it","pt"] else "es"
    try:
        tts = gTTS(text=reply_text, lang=tts_lang)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al generar el audio: {e}")
        audio_base64 = ""

    return jsonify({"reply": reply_text, "audio": audio_base64})

# Endpoint Stripe: Donaciones
@app.route("/create-donation-session", methods=["POST"])
def create_donation_session():
    try:
        data = request.json
        amount = int(data.get("amount", 0)) * 100  # convertir a centavos USD
        if amount < 50:  # Monto mínimo $0.50
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

# Endpoint Stripe: Pago de servicio
@app.route("/create-service-session", methods=["POST"])
def create_service_session():
    try:
        data = request.json
        amount = int(data.get("amount", 0)) * 100  # monto en centavos
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
