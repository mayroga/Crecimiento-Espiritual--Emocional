from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from langdetect import detect
from gtts import gTTS
import base64
from io import BytesIO
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configura tu API Key de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

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
        prompt = f"""
Actúa como guía espiritual y emocional. 
1. Saluda al usuario antes de cualquier cosa y pregunta: "¿Cómo puedo ayudarte hoy?"
2. No juzgues el mensaje del usuario.
3. Si hay desacuerdo o tema conflictivo, conviértelo en un debate constructivo.
4. Si el mensaje es ilegal, dañino o prohibido para la sociedad, evita mencionarlo directamente y redirige inteligentemente hacia lo positivo.
5. Responde siempre en el idioma detectado.
Usuario dice: {user_msg}
"""
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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
