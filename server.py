import os
from flask import Flask, request, jsonify, send_from_directory, Response
from google import genai

app = Flask(__name__, static_folder='public', static_url_path='')

# Inicialización segura para la API Key de formato 'AIza'
api_key_env = os.environ.get('GEMINI_API_KEY')
client = genai.Client(api_key=api_key_env)

@app.route('/')
def index():
    return send_from_directory('public', 'index.html')

def empaquetar_contexto(data):
    descripcion = data.get('descripcion', '')
    contexto = f"OBJETIVO / DESCRIPCIÓN DEL SISTEMA:\n{descripcion}\n\n"
    contexto += "=== ARCHIVOS ACTUALES ===\n"
    for i in range(1, 6):
        nombre = data.get(f'nombre{i}', f'Archivo_{i}').strip()
        contenido = data.get(f'codigo{i}', '').strip()
        if nombre or contenido:
            contexto += f"[{nombre if nombre else f'Archivo_{i}'}]\n{contenido}\n\n"
    return contexto

# NUEVO MÓDULO: EXPLORACIÓN Y CONSULTAS (Fase de Diseño y Sugerencias)
@app.route('/explorar_app', methods=['POST'])
def explorar_app():
    contexto_usuario = empaquetar_contexto(request.get_json())
    prompt = f"""
    Eres un Consultor de Software Senior y Arquitecto de Información. Tu objetivo es procesar toda la información desorganizada o ideas que el usuario introdujo en la descripción.
    
    INSTRUCCIONES DE EXPLORACIÓN:
    1. Organiza las ideas del usuario, extrae los requerimientos reales del sistema y dale una lógica de software coherente.
    2. Infiere y sugiere detalladamente qué tipo de aplicación o arquitectura le conviene construir (tecnologías recomendadas, estructura de archivos y base de datos).
    3. NO generes código en los paneles de archivos. Todo tu análisis y sugerencias conceptuales deben ir estrictamente en la sección final.
    
    Devuelve la respuesta estructurada EXACTAMENTE de esta manera para mantener la consistencia con el frontend:
    :::INICIO_SUGERENCIAS:::
    ### 🧠 INFORME DE EXPLORACIÓN DE SISTEMA Y CONSULTA ARQUITECTÓNICA
    
    #### 1. REQUERIMIENTOS CLAVE DETECTADOS (INFORMACIÓN ORGANIZADA):
    (Sintetiza la información caótica del usuario en puntos limpios y lógicos)
    
    #### 2. INFERENCIA Y PROPUESTA DE ARQUITECTURA:
    (Sugiere cuántos archivos se necesitan, qué nombres ponerles y qué lenguaje usar para máxima eficiencia en RAM)
    
    #### 3. MAPA DE RUTA DE INGENIERÍA:
    (Explica el proceso paso a paso de lo que se va a construir, qué coger, qué herramientas evitar en plataformas como Render y cómo proceder)
    :::FIN_SUGERENCIAS:::
    """ + contexto_usuario

    return Response(generar_stream(prompt), mimetype='text/plain')

# MÓDULO: CREAR APLICACIONES
@app.route('/crear_app', methods=['POST'])
def crear_app():
    contexto_usuario = empaquetar_contexto(request.get_json())
    prompt = f"""
    Eres un Arquitecto de Software Senior y Maestro de Codificación. Tu tarea es CREAR el sistema o los códigos solicitados.
    
    INSTRUCCIONES DE ALTA PRECISIÓN:
    1. Diseña un sistema donde todos los archivos estén milimétricamente ALINEADOS y RELACIONADOS entre sí.
    2. Genera los códigos completos, funcionales, optimizados para RAM y sin errores.
    
    Devuelve la respuesta usando EXACTAMENTE este formato divisor:
    :::INICIO_ARCHIVO:::Nombre_Del_Archivo.extension
    (Código completo sin usar markdown)
    :::FIN_ARCHIVO:::
    
    :::INICIO_SUGERENCIAS:::
    (Explicación del proceso y despliegue del sistema completo generado)
    :::FIN_SUGERENCIAS:::
    """ + contexto_usuario
    return Response(generar_stream(prompt), mimetype='text/plain')

# MÓDULO: REVISIÓN DE APLICACIONES
@app.route('/revisar_app', methods=['POST'])
def revisar_app():
    contexto_usuario = empaquetar_contexto(request.get_json())
    prompt = f"""
    Eres un Auditor de Seguridad y Optimización de Código. Tu tarea es analizar de forma crítica los códigos provistos por el usuario.
    Devuelve el resultado con este formato estricto:
    :::INICIO_SUGERENCIAS:::
    ### REPORTE DE INGENIERÍA DE ALTA PRECISIÓN
    1. ANÁLISIS DE ERRORES DETECTADOS
    2. CÓDIGOS CORREGIDOS Y ALINEADOS
    3. GUÍA MAESTRA DE DESPLIEGUE
    :::FIN_SUGERENCIAS:::
    """ + contexto_usuario
    return Response(generar_stream(prompt), mimetype='text/plain')

# MÓDULO: CORRECCIÓN DE CÓDIGOS EXPRESS
@app.route('/corregir_app', methods=['POST'])
def corregir_app():
    contexto_usuario = empaquetar_contexto(request.get_json())
    prompt = f"""
    Eres un Compilador y Corrector Mecánico Ultra-Preciso. Repara errores mecánicos: sintaxis rota, comas, corchetes o llaves faltantes. 
    Está estrictamente PROHIBIDO inventar lógica nueva o agregar características no solicitadas.
    Devuelve cada archivo corregido utilizando estrictamente este formato divisor:
    :::INICIO_ARCHIVO:::Nombre_Del_Archivo.extension
    (Código original formateado sin markdown)
    :::FIN_ARCHIVO:::
    :::INICIO_SUGERENCIAS:::
    ✓ Corrección Mecánica Profesional Exitosa.
    :::FIN_SUGERENCIAS:::
    """ + contexto_usuario
    return Response(generar_stream(prompt), mimetype='text/plain')

def generar_stream(prompt):
    try:
        response_stream = client.models.generate_content_stream(
            model='gemini-2.5-flash',
            contents=prompt
        )
        for chunk in response_stream:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f":::INICIO_SUGERENCIAS:::\nError de conexión con el motor de IA en Render: {str(e)}\n:::FIN_SUGERENCIAS:::"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
