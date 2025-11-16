from flask import Flask, render_template, jsonify
import sqlite3

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend', static_url_path='/frontend')

DB_PATH = 'backend/database/buildsensei.db'

def get_components(component_type):
    """Retorna lista de componentes desde la base de datos según el tipo."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"SELECT name FROM {component_type}"
    cursor.execute(query)
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/cpus')
def get_cpus():
    cpus = get_components('cpu')
    return jsonify(cpus)

@app.route('/api/gpus')
def get_gpus():
    gpus = get_components('video_card')
    return jsonify(gpus)

if __name__ == '__main__':
    app.run(debug=True)
