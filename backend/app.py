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
# DICCIONARIO DE CONSUMO DE GPU (TDP en Watts)
# ------------------------------------------------
GPU_POWER_CONSUMPTION = {
    # NVIDIA RTX 50 Series
    'RTX 5090': 575,
    'RTX 5080': 320,
    'RTX 5070 Ti': 320,
    'RTX 5070': 250,
    'RTX 5060 Ti': 190,
    'RTX 5060': 170,
    
    # NVIDIA RTX 40 Series
    'RTX 4090': 450,
    'RTX 4080 SUPER': 320,
    'RTX 4080': 320,
    'RTX 4070 Ti SUPER': 285,
    'RTX 4070 Ti': 285,
    'RTX 4070 SUPER': 220,
    'RTX 4070': 200,
    'RTX 4060 Ti': 130,
    'RTX 4060': 115,
    
    # NVIDIA RTX 30 Series
    'RTX 3090': 420,
    'RTX 3080 Ti': 420,
    'RTX 3080 10GB': 320,
    'RTX 3070': 220,
    'RTX 3060 Ti': 210,
    'RTX 3060 12GB': 170,
    'RTX 3050': 70,
    'RTX 3050 6GB': 70,
    'RTX 3050 8GB': 70,
    
    # AMD RX 9000 Series
    'RX 9070 XT': 420,
    'RX 9070': 340,
    'RX 9060 XT': 210,
    
    # AMD RX 7000 Series
    'RX 7900 XTX': 420,
    'RX 7900 XT': 380,
    'RX 7900': 380,
    'RX 7800 XT': 310,
    'RX 7700 XT': 250,
    'RX 7600 XT': 190,
    'RX 7600': 100,
    
    # AMD RX 6000 Series
    'RX 6800 XT': 305,
    'RX 6800': 250,
    'RX 6750 XT': 250,
    'RX 6700 XT': 230,
    'RX 6600': 110,
    'RX 6500 XT': 107,
    
    # Intel Arc
    'Arc B580': 190,
    
    # NVIDIA Legacy
    'GTX 1660 SUPER': 125,
    'GT 710': 19,
    
    # NVIDIA Professional
    'RTX 6000 Ada Generation': 320,
    'RTX A5000': 250,
}


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


def get_gpu_power(gpu_name):
    """
    Obtiene el consumo de potencia aproximado (TDP) de una GPU.
    Busca coincidencias en el diccionario de manera flexible.
    """
    if not gpu_name:
        return 0
    
    gpu_name_upper = gpu_name.upper()
    
    # Búsqueda exacta primero
    for model, power in GPU_POWER_CONSUMPTION.items():
        if model.upper() == gpu_name_upper:
            return power
    
    # Búsqueda parcial (mejor coincidencia)
    best_match = None
    best_match_len = 0
    
    for model, power in GPU_POWER_CONSUMPTION.items():
        if model.upper() in gpu_name_upper:
            if len(model) > best_match_len:
                best_match = power
                best_match_len = len(model)
    
    if best_match is not None:
        return best_match
    
    # Valores por defecto según heurística
    if any(x in gpu_name_upper for x in ['RTX 4090', 'RTX 3090', 'RTX 5090']):
        return 450
    elif any(x in gpu_name_upper for x in ['RTX 408', 'RTX 308', 'RTX 508', 'RX 7900', 'RX 9070 XT']):
        return 320
    elif any(x in gpu_name_upper for x in ['RTX 407', 'RTX 307', 'RTX 507', 'RX 7800', 'RX 9060']):
        return 250
    else:
        return 150  # Valor por defecto conservador


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
            "value": name  # ✅ Enviar el nombre (lo que existe en BD)
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
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, wattage FROM power_supply")

    psus = []
    for name, wattage in cursor.fetchall():
        psus.append({
            "label": f"{name} - {wattage}W",
            "value": name
        })

    conn.close()
    return jsonify(psus)


# ------------------------------------------------
# COMPATIBILIDAD
# ------------------------------------------------
@app.route("/api/check-compatibility", methods=["GET"])
def check_compatibility():
    cpu = request.args.get("cpu")
    gpu = request.args.get("gpu")  # Este es el NAME de la GPU
    motherboard = request.args.get("motherboard")
    memory = request.args.get("memory")
    psu = request.args.get("psu")

    print(f"\n=== DEBUG CHECK-COMPATIBILITY ===")
    print(f"GPU recibida: {gpu}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # GPU - Buscar por NAME y obtener CHIPSET
    cursor.execute("SELECT chipset FROM video_card WHERE name = ?", (gpu,))
    gpu_data = cursor.fetchone()
    if not gpu_data:
        return jsonify({"error": "GPU no encontrada"}), 400
    gpu_chipset = gpu_data[0]
    print(f"GPU Name: {gpu}")
    print(f"GPU Chipset: {gpu_chipset}")

    # Ahora usar el CHIPSET para buscar el TDP
    gpu_power_tdp = get_gpu_power(gpu_chipset)
    
    # CPU
    cursor.execute("SELECT microarchitecture FROM cpu WHERE name = ?", (cpu,))
    cpu_data = cursor.fetchone()
    if not cpu_data:
        return jsonify({"error": "CPU no encontrada"}), 400
    cpu_microarch = cpu_data[0]
    print(f"CPU Microarch: {cpu_microarch}")

    # Motherboard
    cursor.execute("SELECT socket, max_memory, memory_slots FROM motherboard WHERE name = ?", (motherboard,))
    mb = cursor.fetchone()
    if not mb:
        return jsonify({"error": "Motherboard no encontrada"}), 400
    mb_socket, mb_max_memory, mb_slots = mb
    print(f"MB Socket: {mb_socket}, Max Memory: {mb_max_memory}, Slots: {mb_slots}")

    # PSU
    cursor.execute("SELECT wattage FROM power_supply WHERE name = ?", (psu,))
    psu_data = cursor.fetchone()
    if not psu_data:
        return jsonify({"error": "PSU no encontrada"}), 400
    psu_wattage = safe_number(psu_data[0])
    print(f"PSU Wattage: {psu_wattage}")

    # RAM
    cursor.execute("SELECT modules FROM memory WHERE name = ?", (memory,))
    ram_data = cursor.fetchone()
    if not ram_data:
        return jsonify({"error": "Memoria no encontrada"}), 400
    modules = ram_data[0]
    module_count = extract_module_count(modules)
    if module_count is None:
        return jsonify({"error": f"No se pudo interpretar la cantidad de módulos RAM: '{modules}'"}), 400
    print(f"RAM Modules: {module_count}")

    # ------------------------------------------------
    # VALIDACIONES
    # ------------------------------------------------
    issues = []
    warnings = []

    # CPU ↔ Motherboard usando deduce_socket
    cpu_socket = deduce_socket(cpu_microarch)
    print(f"\nCPU Socket deducido: {cpu_socket}")
    if cpu_socket is None:
        issues.append(f"No se pudo determinar el socket del CPU ({cpu_microarch}).")
    elif cpu_socket.lower() != mb_socket.lower():
        issues.append(f"El CPU ({cpu}) requiere socket {cpu_socket}, pero la motherboard usa {mb_socket}.")

    # RAM ↔ Motherboard
    if module_count > mb_slots:
        issues.append(f"La RAM usa {module_count} módulos, pero la motherboard solo tiene {mb_slots} slots.")

    # PSU ↔ GPU (análisis mejorado con TDP)
    cpu_power_tdp = 125  # TDP estimado por defecto para CPUs
    
    total_power_needed = gpu_power_tdp + cpu_power_tdp
    required_psu = total_power_needed * 1.25  # Margen de seguridad del 25%
    
    print(f"\n=== ANÁLISIS DE POTENCIA ===")
    print(f"GPU: {gpu}")
    print(f"GPU Power TDP: {gpu_power_tdp}W")
    print(f"CPU Power TDP: {cpu_power_tdp}W")
    print(f"Total Power Needed: {total_power_needed}W")
    print(f"Required PSU (con 25% margen): {int(required_psu)}W")
    print(f"PSU Available: {psu_wattage}W")
    print(f"Compatible: {psu_wattage >= required_psu}")
    
    if psu_wattage < required_psu:
        issues.append(
            f"PSU insuficiente. GPU ({gpu_power_tdp}W TDP) + CPU ({cpu_power_tdp}W TDP) = {total_power_needed}W. "
            f"Se recomienda PSU de {int(required_psu)}W (con 25% margen), pero tienes {psu_wattage}W."
        )
    elif psu_wattage < total_power_needed * 1.5:
        warnings.append(
            f"PSU justa. Considere una PSU más potente. Consumo estimado: {total_power_needed}W, "
            f"PSU actual: {psu_wattage}W (margen: {psu_wattage - total_power_needed}W)."
        )

    conn.close()

    # ------------------------------------------------
    # RESULTADO
    # ------------------------------------------------
    result = {
        "compatible": len(issues) == 0,
        "power_analysis": {
            "gpu_power_tdp": gpu_power_tdp,
            "cpu_power_tdp": cpu_power_tdp,
            "total_estimated": total_power_needed,
            "psu_available": psu_wattage,
            "margin": psu_wattage - total_power_needed
        }
    }
    
    if len(issues) == 0:
        result["message"] = "✔️ Todos los componentes son compatibles."
    else:
        result["issues"] = issues
    
    if warnings:
        result["warnings"] = warnings
    
    print(f"\nResultado: {result}\n")
    
    return jsonify(result)


# ------------------------------------------------
# MAIN
# ------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
