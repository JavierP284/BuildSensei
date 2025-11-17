from flask import Flask, render_template, jsonify, request 
import sqlite3

app = Flask(
    __name__,
    template_folder='../frontend',
    static_folder='../frontend',
    static_url_path='/frontend'
)

DB_PATH = 'backend/database/buildsensei.db'


# ------------------------------------------------
# FUNCIONES DE LIMPIEZA
# ------------------------------------------------
def safe_number(value):
    if value is None:
        return None

    if isinstance(value, str):
        value = value.replace(",", ".").strip()

    try:
        num = float(value)
        if num.is_integer():
            return int(num)
        return num
    except ValueError:
        return None


def extract_module_count(modules_str):
    """
    Extrae la cantidad de módulos desde cadenas como:
    "2 x 8GB", "2x8GB", "2 ,16 x 8GB", "1 X 16 GB", etc.
    """
    if not modules_str:
        return None

    part = modules_str.lower().split("x")[0]
    part = part.replace(",", ".").strip()
    return safe_number(part)


# ------------------------------------------------
# CONEXIÓN A BD
# ------------------------------------------------
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_components(component_type):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM {component_type}")
    items = [row[0] for row in cursor.fetchall()]
    conn.close()
    return items


# ------------------------------------------------
# FUNCIONES DE COMPATIBILIDAD
# ------------------------------------------------
def deduce_socket(microarch):
    microarch = microarch.lower()
    if "zen 4" in microarch:
        return "AM5"
    if "zen" in microarch:
        return "AM4"
    if "raptor" in microarch or "alder" in microarch:
        return "LGA1700"
    if "comet" in microarch or "rocket" in microarch:
        return "LGA1200"
    if "coffee" in microarch or "kaby" in microarch or "skylake" in microarch:
        return "LGA1151"
    return None


# ------------------------------------------------
# RUTAS DE CARGA DE SELECTS
# ------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/cpus')
def get_cpus():
    return jsonify(get_components('cpu'))


@app.route('/api/gpus')
def get_gpus():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, chipset FROM video_card")

    gpus = []
    for name, chipset in cursor.fetchall():
        gpus.append({
            "label": f"{chipset} - {name}",
            "value": name
        })

    conn.close()
    return jsonify(gpus)


@app.route('/api/motherboards')
def get_motherboards():
    return jsonify(get_components('motherboard'))


@app.route('/api/memory')
def get_memory():
    return jsonify(get_components('memory'))


@app.route('/api/psus')
def get_psus():
    return jsonify(get_components('power_supply'))


# ------------------------------------------------
# COMPATIBILIDAD
# ------------------------------------------------
@app.route("/api/check-compatibility", methods=["GET"])
def check_compatibility():
    cpu = request.args.get("cpu")
    gpu = request.args.get("gpu")
    motherboard = request.args.get("motherboard")
    memory = request.args.get("memory")
    psu = request.args.get("psu")

    conn = get_db_connection()
    cursor = conn.cursor()

    # CPU
    cursor.execute("SELECT microarchitecture FROM cpu WHERE name = ?", (cpu,))
    cpu_data = cursor.fetchone()
    if not cpu_data:
        return jsonify({"error": "CPU no encontrada"}), 400
    cpu_microarch = cpu_data[0]

    # Motherboard
    cursor.execute("SELECT socket, max_memory, memory_slots FROM motherboard WHERE name = ?", (motherboard,))
    mb = cursor.fetchone()
    if not mb:
        return jsonify({"error": "Motherboard no encontrada"}), 400
    mb_socket, mb_max_memory, mb_slots = mb

    # GPU
    cursor.execute("SELECT name FROM video_card WHERE name = ?", (gpu,))
    if not cursor.fetchone():
        return jsonify({"error": "GPU no encontrada"}), 400

    # PSU
    cursor.execute("SELECT wattage FROM power_supply WHERE name = ?", (psu,))
    psu_data = cursor.fetchone()
    if not psu_data:
        return jsonify({"error": "PSU no encontrada"}), 400
    psu_wattage = safe_number(psu_data[0])

    # RAM
    cursor.execute("SELECT modules FROM memory WHERE name = ?", (memory,))
    ram_data = cursor.fetchone()
    if not ram_data:
        return jsonify({"error": "Memoria no encontrada"}), 400
    modules = ram_data[0]
    module_count = extract_module_count(modules)
    if module_count is None:
        return jsonify({"error": f"No se pudo interpretar la cantidad de módulos RAM: '{modules}'"}), 400

    # ------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------
    issues = []

    # CPU ↔ Motherboard usando deduce_socket
    cpu_socket = deduce_socket(cpu_microarch)
    if cpu_socket is None:
        issues.append(f"No se pudo determinar el socket del CPU ({cpu_microarch}).")
    elif cpu_socket.lower() != mb_socket.lower():
        issues.append(f"El CPU ({cpu}) requiere socket {cpu_socket}, pero la motherboard usa {mb_socket}.")

    # RAM ↔ Motherboard
    if module_count > mb_slots:
        issues.append(f"La RAM usa {module_count} módulos, pero la motherboard solo tiene {mb_slots} slots.")

    # PSU ↔ GPU (check básico)
    if psu_wattage < 450:
        issues.append(f"La PSU es muy débil ({psu_wattage}W). Se recomiendan al menos 450W para GPUs modernas.")

    conn.close()

    # ------------------------------------------------
    # RESULTADO
    # ------------------------------------------------
    if len(issues) == 0:
        return jsonify({"compatible": True, "message": "Todos los componentes son compatibles."})
    return jsonify({"compatible": False, "issues": issues})


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
