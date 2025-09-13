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

# Configura tu API Key de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configura Stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

@app.route("/")
def home():
    return render_template("index.html", title="Crecimiento Espiritual-Emocional")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"reply": "Por favor escribe algo.", "audio": ""})

    # Detecta idioma
    try:
        idioma = detect(user_msg)
    except:
        idioma = "es"

    # Detección básica de religión
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

    # Generación de respuesta con Gemini IA
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Saluda primero al usuario y ofrece ayuda espiritual antes de responder. Actúa como guía espiritual {religion}. Responde en {idioma}. Usuario dice: {user_msg}"
        response = model.generate_content(prompt)
        reply_text = response.text
    except Exception as e:
        print(f"Error al llamar a la API de Gemini: {e}")
        reply_text = "Lo siento, hubo un problema al generar la respuesta. Por favor, inténtalo de nuevo más tarde."

    # Convertir texto a voz (TTS)
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

@app.route("/create-donation-session", methods=["POST"])
def create_donation_session():
    data = request.json
    amount = float(data.get("amount", 0))
    if amount < 4.99:
        return jsonify({"error": "La donación mínima es $4.99"}), 400

    amount_cents = int(amount * 100)

    try:
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
            success_url="https://tuweb.com/gracias",
            cancel_url="https://tuweb.com/cancelado",
        )
        return jsonify({"url": session.url})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
