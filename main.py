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

# =======================================================
# CORS: autorización específica para Google Sites, Stripe, OpenAI, Gemini y Render
# =======================================================
URL_SITE = "https://crecimiento-espiritual-emocional.onrender.com"
CORS(app, origins=[
    "https://sites.google.com/view/felicidad/",
    "https://checkout.stripe.com",
    "https://api.openai.com",
    "https://gemini.googleapis.com",
    URL_SITE
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
# RUTAS DE CHAT Y TTS
# =======================================================
@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    if not user_msg:
        return jsonify({"reply": "Por favor escribe algo.", "audio": ""})

    # Detectar idioma automáticamente
    try:
        idioma_detectado = detect(user_msg)
    except:
        idioma_detectado = "es"

    # Validar idioma para gTTS
    gtts_map = {
        "es": "es",
        "en": "en",
        "fr": "fr",
        "de": "de",
        "it": "it",
        "pt": "pt"
    }
    idioma = gtts_map.get(idioma_detectado[:2], "es")

    # Detectar religión según palabras clave
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

    # Generar respuesta de IA
    try:
        system_prompt = f"Eres un guía espiritual de crecimiento emocional. Tu único propósito es ayudar al usuario a encontrar paz y propósito a través de la religión o el crecimiento espiritual. Responde siempre de forma amable y cálida en {idioma}. El tema principal es el crecimiento espiritual {religion}."
        if USE_OPENAI:
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ]
            )
            reply_text = response.choices[0].message.content
        else:
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"{system_prompt} Usuario dice: {user_msg}"
            response = model.generate_content(prompt)
            reply_text = response.text
    except Exception as e:
        print(f"Error al llamar a la API de IA: {e}")
        reply_text = "Lo siento, hubo un problema al generar la respuesta. Por favor, inténtalo de nuevo más tarde."

    # Generación de audio con gTTS
    try:
        tts = gTTS(text=reply_text, lang=idioma)
        mp3_fp = BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')
    except Exception as e:
        print(f"Error al generar el audio: {e}")
        audio_base64 = ""

    return jsonify({"reply": reply_text, "audio": audio_base64})

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
            success_url="https://tuweb.com/gracias",
            cancel_url="https://tuweb.com/cancelado",
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
                    "unit_amount": 1000,
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
