from flask import Flask, render_template, jsonify, request 
import sqlite3
from gpu_benchmarks import get_gpu_benchmark_url  # ← Nueva importación

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


# ---------------------------
# NUEVA FUNCIÓN: BOTTLENECK
# ---------------------------
def detect_bottleneck(cpu_cores, cpu_boost_ghz, cpu_tdp, gpu_tdp, gpu_chipset=None):
    """
    Heurística ajustada para detectar cuellos de botella.
    Devuelve: { result, summary, details }
    Ajustes principales:
     - Umbrales menos sensibles para marcar "CPU significativamente superior".
     - Regla explícita de "balanced" para CPUs y GPUs de muy alta gama.
     - Summary legible y detalles numéricos separados.
    """
    cpu_cores = int(cpu_cores) if cpu_cores else 0
    cpu_boost = float(cpu_boost_ghz) if cpu_boost_ghz else 0.0
    cpu_tdp = safe_number(cpu_tdp) or 0
    gpu_tdp = safe_number(gpu_tdp) or 0

    cpu_score = cpu_cores * cpu_boost  # proxy simple: core-GHz
    gpu_score = gpu_tdp

    # Regla explícita: combos de muy alta gama se consideran balanceados
    if cpu_score >= 80 and gpu_score >= 400:
        return {
            "result": "no_significant_bottleneck",
            "summary": "Combo de alta gama: no se detecta un cuello de botella significativo.",
            "details": {"cpu_score": round(cpu_score,1), "gpu_tdp": gpu_tdp, "cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost}
        }

    # Casos claros (CPU limita GPU)
    if cpu_cores <= 4 and gpu_tdp >= 300:
        return {
            "result": "possible_cpu_bottleneck",
            "summary": "La CPU podría limitar el rendimiento frente a esta GPU (CPU con pocos núcleos).",
            "details": {"cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "cpu_tdp": cpu_tdp, "gpu_tdp": gpu_tdp, "note": "GPU de alta demanda vs CPU con pocos núcleos."}
        }

    if cpu_boost < 3.5 and gpu_tdp >= 350:
        return {
            "result": "possible_cpu_bottleneck",
            "summary": "La frecuencia de la CPU puede ser limitada para esta GPU.",
            "details": {"cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "cpu_tdp": cpu_tdp, "gpu_tdp": gpu_tdp, "note": "Frecuencia boost baja vs GPU potente."}
        }

    # GPU limita CPU — regla para detectar GPU débiles frente a CPUs muy potentes
    if cpu_cores >= 10 and gpu_tdp <= 200:
        return {
            "result": "possible_gpu_bottleneck",
            "summary": "La GPU podría limitar el rendimiento frente a esta CPU.",
            "details": {"cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "cpu_tdp": cpu_tdp, "gpu_tdp": gpu_tdp, "note": "CPU relativamente potente vs GPU de baja demanda."}
        }

    # Heurística general: relación CPU/GPU (menos sensible)
    rel = cpu_score / max(1.0, gpu_score/50.0)  # normaliza gpu_tdp a escala similar

    # Si la relación es muy alta, posible GPU bottleneck (umbral elevado)
    if rel > 12.0:
        return {
            "result": "possible_gpu_bottleneck",
            "summary": "La CPU es mucho más potente que la GPU; la GPU podría ser el cuello de botella.",
            "details": {"cpu_score": round(cpu_score,1), "gpu_tdp": gpu_tdp, "cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "note": "Relación CPU/GPU elevada."}
        }

    # Si la relación es muy baja, posible CPU bottleneck (umbral más estricto)
    if gpu_score > 0 and rel < 1.8:
        return {
            "result": "possible_cpu_bottleneck",
            "summary": "La relación CPU/GPU sugiere que la CPU podría limitar el rendimiento en algunos escenarios.",
            "details": {"cpu_score": round(cpu_score,1), "gpu_tdp": gpu_tdp, "cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "note": "Relación aproximada entre capacidad CPU y demanda GPU."}
        }

    return {
        "result": "no_significant_bottleneck",
        "summary": "No se detecta un cuello de botella evidente entre CPU y GPU.",
        "details": {"cpu_cores": cpu_cores, "cpu_boost_ghz": cpu_boost, "cpu_tdp": cpu_tdp, "gpu_tdp": gpu_tdp}
    }

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
    """
    Deduce el socket del CPU basándose en la microarquitectura.
    Cubre todas las arquitecturas presentes en la BD.
    """
    if not microarch:
        return None
    
    microarch = microarch.lower().strip()
    
    # ===== AMD SOCKETS =====
    # Zen 5 y más nuevos -> AM5
    if "zen 5" in microarch:
        return "AM5"
    
    # Zen 4 -> AM5
    if "zen 4" in microarch:
        return "AM5"
    
    # Zen 3 -> AM4
    if "zen 3" in microarch:
        return "AM4"
    
    # Zen 2 -> AM4
    if "zen 2" in microarch:
        return "AM4"
    
    # Zen+ y Zen (primera gen) -> AM4
    if "zen+" in microarch or (microarch == "zen" and "zen 2" not in microarch and "zen 3" not in microarch and "zen 4" not in microarch and "zen 5" not in microarch):
        return "AM4"
    
    # Piledriver, Steamroller, Excavator (FX, A-series) -> AM3+ o variantes
    if any(x in microarch for x in ["piledriver", "steamroller", "excavator"]):
        return "AM3+"
    
    # Bulldozer -> AM3+
    if "bulldozer" in microarch:
        return "AM3+"
    
    # K10, Lynx (antiguos) -> AM2+/AM3
    if any(x in microarch for x in ["k10", "lynx"]):
        return "AM2+"
    
    # Jaguar (Athlon X4) -> FP2
    if "jaguar" in microarch:
        return "FP2"
    
    # Puma+ -> FP2
    if "puma+" in microarch:
        return "FP2"
    
    # ===== INTEL SOCKETS =====
    # Raptor Lake Refresh, Raptor Lake -> LGA1700
    if any(x in microarch for x in ["raptor lake", "raptor"]):
        return "LGA1700"
    
    # Arrow Lake -> LGA1851
    if "arrow lake" in microarch:
        return "LGA1851"
    
    # Alder Lake -> LGA1700
    if "alder lake" in microarch:
        return "LGA1700"
    
    # Rocket Lake -> LGA1200
    if "rocket lake" in microarch:
        return "LGA1200"
    
    # Comet Lake -> LGA1200
    if "comet lake" in microarch:
        return "LGA1200"
    
    # Coffee Lake, Coffee Lake Refresh -> LGA1151 (rev 2)
    if "coffee lake" in microarch:
        return "LGA1151"
    
    # Kaby Lake -> LGA1151
    if "kaby lake" in microarch:
        return "LGA1151"
    
    # Skylake -> LGA1151
    if "skylake" in microarch:
        return "LGA1151"
    
    # Broadwell -> LGA1150
    if "broadwell" in microarch:
        return "LGA1150"
    
    # Haswell -> LGA1150
    if "haswell" in microarch:
        return "LGA1150"
    
    # Ivy Bridge -> LGA1155
    if "ivy bridge" in microarch:
        return "LGA1155"
    
    # Sandy Bridge -> LGA1155
    if "sandy bridge" in microarch:
        return "LGA1155"
    
    # Nehalem, Westmere -> LGA1156/LGA1366
    if any(x in microarch for x in ["nehalem", "westmere"]):
        return "LGA1156"
    
    # Core (antiga), Wolfdale, Yorkfield -> LGA775
    if any(x in microarch for x in ["core", "wolfdale", "yorkfield"]):
        return "LGA775"
    
    # Pentium 4 y Celeron antiguos
    if any(x in microarch for x in ["pentium e", "pentium g", "celeron e", "celeron g"]):
        if "e2" in microarch or "e5" in microarch or "e6" in microarch:
            return "LGA775"
        if "e3" in microarch or "g3" in microarch or "g4" in microarch or "g5" in microarch or "g6" in microarch:
            return "LGA1155"
    
    # Xeon antiguos
    if "xeon" in microarch:
        if any(x in microarch for x in ["e5", "e3"]):
            return "LGA1155" if "e3" in microarch else "LGA2011"
        if "e2" in microarch:
            return "LGA1151"
    
    # Por defecto si no se puede determinar
    print(f"[SOCKET] No se pudo determinar socket para: {microarch}")
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
            "value": chipset  # ← Cambiar de 'name' a 'chipset'
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
    gpu = request.args.get("gpu")  # Ahora es el CHIPSET, no el NAME
    motherboard = request.args.get("motherboard")
    memory = request.args.get("memory")
    psu = request.args.get("psu")

    print(f"\n=== DEBUG CHECK-COMPATIBILITY ===")
    print(f"GPU recibida: {gpu}")

    conn = get_db_connection()
    cursor = conn.cursor()

    # GPU - Buscar por CHIPSET en lugar de NAME
    cursor.execute("SELECT name FROM video_card WHERE chipset = ?", (gpu,))
    gpu_row = cursor.fetchone()
    if not gpu_row:
        return jsonify({"error": "GPU no encontrada"}), 400
    gpu_name = gpu_row[0]
    gpu_chipset = gpu  # Ya tenemos el chipset
    
    gpu_power_tdp = get_gpu_power(gpu_chipset)

    # CPU - obtener microarch + cores + boost + tdp
    cursor.execute("SELECT microarchitecture, core_count, boost_clock, tdp FROM cpu WHERE name = ?", (cpu,))
    cpu_row = cursor.fetchone()
    if not cpu_row:
        return jsonify({"error": "CPU no encontrada"}), 400
    cpu_microarch, cpu_core_count, cpu_boost_clock, cpu_tdp = cpu_row
    print(f"CPU Microarch: {cpu_microarch}, cores: {cpu_core_count}, boost: {cpu_boost_clock}, tdp: {cpu_tdp}")

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
    # Asegurar que mb_slots es un número entero
    mb_slots_int = safe_number(mb_slots) if mb_slots else 0
    if not isinstance(mb_slots_int, int) or mb_slots_int <= 0:
        mb_slots_int = int(mb_slots_int) if mb_slots_int else 0
    
    module_count_int = int(module_count) if module_count else 0
    
    print(f"RAM Module Count: {module_count_int}, MB Slots: {mb_slots_int}")
    
    if module_count_int > mb_slots_int:
        issues.append(
            f"Incompatibilidad de RAM: Se requieren {module_count_int} módulos, "
            f"pero la motherboard solo tiene {mb_slots_int} slots."
        )
    elif module_count_int == mb_slots_int and mb_slots_int > 0:
        #  CAMBIO: Esto es compatible, solo agregar warning
        warnings.append(
            f"Uso máximo de slots: La RAM usa todos los {mb_slots_int} slots disponibles. "
            f"No hay espacio para ampliación futura."
        )
    elif module_count_int < mb_slots_int:
        #  Compatibles con espacio libre
        free_slots = mb_slots_int - module_count_int
        if free_slots == 1:
            warnings.append(
                f"Slot disponible: La RAM usa {module_count_int} de {mb_slots_int} slots. "
                f"Queda 1 slot libre para ampliación."
            )
        else:
            # Sin warning si hay 2+ slots libres
            pass

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
            f"PSU ajustada. Consumo estimado: {total_power_needed}W, "
            f"PSU actual: {psu_wattage}W (margen: {int(psu_wattage - total_power_needed)}W)."
        )

    # -----------------------------
    # Calcular análisis de bottleneck
    # -----------------------------
    bottleneck = detect_bottleneck(cpu_core_count, cpu_boost_clock, cpu_tdp, gpu_power_tdp, gpu_chipset)

    # Obtener URL de benchmark
    gpu_benchmark_url = get_gpu_benchmark_url(gpu_chipset)

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
            "psu_available": int(psu_wattage),
            "margin": int(psu_wattage - total_power_needed)
        },
        "memory_analysis": {
            "modules_required": int(module_count),
            "slots_available": int(mb_slots_int)
        },
        "bottleneck_analysis": bottleneck,
        "gpu_benchmark": {
            "chipset": gpu_chipset,
            "url": gpu_benchmark_url
        }
    }
    
    if len(issues) == 0:
        result["message"] = "Todos los componentes son compatibles."
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
