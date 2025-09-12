from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from langdetect import detect
from gtts import gTTS
import base64
from io import BytesIO

app = Flask(__name__)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html", title="Crecimiento Espiritual-Emocional")

@app.route("/chat", methods=["POST"])
def chat():
    user_msg = request.json.get("message")
    try:
        idioma = detect(user_msg)
    except:
        idioma = "es"
    
    # Detección de religión básica
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

    # Gemini IA
    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Actúa como guía espiritual {religion}. Responde en {idioma}. Usuario dice: {user_msg}"
    response = model.generate_content(prompt)

    # Convertir texto a voz (TTS)
    tts = gTTS(text=response.text, lang=idioma[:2])  # usa los primeros 2 caracteres del código ISO
    mp3_fp = BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio_base64 = base64.b64encode(mp3_fp.read()).decode('utf-8')

    return jsonify({"reply": response.text, "audio": audio_base64})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
