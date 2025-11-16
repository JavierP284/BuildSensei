from flask import Flask, render_template, request

# Le decimos a Flask dónde encontrar las plantillas y los archivos estáticos.
# template_folder: Sube un nivel ('..') y entra a 'frontend'.
# static_folder:   Sube un nivel ('..') y entra a 'frontend'.
# static_url_path: Mantiene la URL para los archivos estáticos como '/frontend' para que coincida con tu HTML.
app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')

# Esta es la ruta principal que muestra el formulario al usuario.
# Corregí la ruta de la plantilla. Flask busca en la carpeta 'templates' por defecto.
@app.route("/")
def index():
    return render_template("index.html")

# Esta ruta ahora solo acepta peticiones POST, que es lo que sucede cuando se envía el formulario.
# Simplificamos la lógica para que procese los datos y muestre los resultados directamente.
@app.route("/evaluar", methods=["POST"])
def evaluar():
    # 1. Recibimos los datos del formulario enviado desde index.html.
    datos_formulario = request.form

    # 2. (Aquí iría tu lógica de sistema experto para evaluar los datos)
    # Por ahora, simplemente pasaremos los datos recibidos a la plantilla de resultados.
    # Por ejemplo, podrías crear un diccionario con los resultados de tu evaluación.
    resultados_evaluacion = {
        "puntaje": 85,
        "comentario": "¡Buena build, pero podrías mejorar el procesador!",
        "datos_recibidos": datos_formulario
    }

    # 3. Renderizamos la plantilla de resultados y le pasamos los datos para que los muestre.
    return render_template("resultados.html", resultados=resultados_evaluacion)

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
