from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/evaluar", methods=["GET","POST"])
def evaluar():
    if request.method == "POST":
        # aquí vendrá la lógica para recibir el formulario y evaluar la build
        data = request.form
        return redirect(url_for("resultados"))
    # por ahora mostramos una página intermedia
    return render_template("index.html")

@app.route("/resultados")
def resultados():
    # por ahora renderiza la plantilla de resultados vacía
    return render_template("resultados.html")

@app.errorhandler(500)
def internal_error(e):
    return render_template("error.html"), 500

if __name__ == "__main__":
    app.run(debug=True)
