from flask import Flask, render_template, request, jsonify
import os
import google.generativeai as genai
from langdetect import detect

app = Flask(__name__)

# Configurar Gemini IA
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
    
    # Detectar religión (básico)
    if any(x in user_msg.lower() for x in ["cristiano", "iglesia", "jesús"]):
        religion = "cristianismo"
    elif any(x in user_msg.lower() for x in ["musulmán", "islam", "mezquita"]):
        religion = "islam"
    else:
        religion = "universal"

    model = genai.GenerativeModel("gemini-pro")
    prompt = f"Actúa como guía espiritual {religion}. Responde en {idioma}. Usuario dice: {user_msg}"
    response = model.generate_content(prompt)
    
    return jsonify({"reply": response.text})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
