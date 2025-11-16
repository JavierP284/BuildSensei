# reglas.py
# Sistema experto para recomendaciones de Motherboard, RAM y PSU
# basado en CPU + GPU proporcionados por el usuario.

# Encabezados disponibles por tabla:
# cpu: name, price, tdp, graphics, core_count, core_clock, boost_clock
# motherboard: name, price, socket, form_factor, max_memory, memory_slots
# memory: name, price, speed, modules, cas_latency
# video_card: name, price, chipset, memory, length
# power_supply: name, price, efficiency, wattage, modular

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "buildsensei.db")


def get_cpu_info(cpu_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, tdp FROM cpu WHERE rowid=?", (cpu_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "tdp": result[1]}
    return None


def get_gpu_info(gpu_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, memory, price FROM video_card WHERE rowid=?", (gpu_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {"name": result[0], "memory": result[1], "price": result[2]}
    return None


# ========================================================================
#  1) TOP 3 MOTHERBOARD RECOMMENDATIONS
# ========================================================================

def recomendar_motherboards(cpu_socket):
    """
    Regla:
    - Motherboard debe tener el mismo socket
    - Las 3 mejores se ordenan por price ASC (más baratas pero compatibles)
    - Con dataset limitado este criterio es estable y simple
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT name, price, socket, form_factor, max_memory, memory_slots
        FROM motherboard
        WHERE socket = ?
        ORDER BY price ASC
        LIMIT 3
    """

    cursor.execute(query, (cpu_socket,))
    results = cursor.fetchall()
    conn.close()

    motherboards = []
    for row in results:
        motherboards.append({
            "name": row[0],
            "price": row[1],
            "socket": row[2],
            "form_factor": row[3],
            "max_memory": row[4],
            "memory_slots": row[5],
        })

    return motherboards


# ========================================================================
#  2) TOP 3 RAM RECOMMENDATIONS
# ========================================================================

def recomendar_ram(max_memory, memory_slots):
    """
    Regla:
    - Memoria debe ser razonable para el equipo
    - Se prioriza:
        > mayor velocidad
        > menor CAS latency
        > mejor precio
    - Se devuelve TOP 3

    NOTA:
    El dataset no especifica DDR4/DDR5, así que filtramos por criterios generales.
    """

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT name, price, speed, modules, cas_latency
        FROM memory
        WHERE speed IS NOT NULL 
        ORDER BY speed DESC, cas_latency ASC, price ASC
        LIMIT 3
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    ram_list = []
    for row in results:
        ram_list.append({
            "name": row[0],
            "price": row[1],
            "speed": row[2],
            "modules": row[3],
            "cas_latency": row[4],
        })

    return ram_list


# ========================================================================
#  3) TOP 3 PSU RECOMMENDATIONS
# ========================================================================

def calcular_consumo_requerido(cpu_tdp, gpu_memory_gb):
    """
    Regla:
    - Se estima el consumo de la GPU según VRAM:
        GPUs 4GB → 75W
        GPUs 6GB → 120W
        GPUs 8GB → 200W
        GPUs 10–12GB → 250W
        GPUs 16GB → 300W
        GPUs 20GB → 350W
        GPUs >20GB → 400W
    - PSU final recomendada = (cpu + gpu) * 1.30
    """

    if gpu_memory_gb <= 4:
        gpu_tdp = 75
    elif gpu_memory_gb <= 6:
        gpu_tdp = 120
    elif gpu_memory_gb <= 8:
        gpu_tdp = 200
    elif gpu_memory_gb <= 12:
        gpu_tdp = 250
    elif gpu_memory_gb <= 16:
        gpu_tdp = 300
    elif gpu_memory_gb <= 20:
        gpu_tdp = 350
    else:
        gpu_tdp = 400

    consumo_total = (cpu_tdp + gpu_tdp) * 1.30
    return int(consumo_total)


def recomendar_psu(cpu_tdp, gpu_memory):
    consumo_requerido = calcular_consumo_requerido(cpu_tdp, gpu_memory)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = """
        SELECT name, price, efficiency, wattage, modular
        FROM power_supply
        WHERE wattage >= ?
        ORDER BY wattage ASC, price ASC
        LIMIT 3
    """

    cursor.execute(query, (consumo_requerido,))
    results = cursor.fetchall()
    conn.close()

    psu_list = []
    for row in results:
        psu_list.append({
            "name": row[0],
            "price": row[1],
            "efficiency": row[2],
            "wattage": row[3],
            "modular": row[4],
            "consumo_requerido": consumo_requerido
        })

    return psu_list


# ========================================================================
# FUNCIÓN PRINCIPAL DEL SISTEMA EXPERTO
# ========================================================================

def ejecutar_sistema_experto(cpu_info, gpu_info, cpu_socket, max_memory=32, memory_slots=2):
    """
    CPU info = {"name":.., "tdp":..}
    GPU info = {"name":.., "memory":..}
    """

    motherboards = recomendar_motherboards(cpu_socket)
    ram_options = recomendar_ram(max_memory, memory_slots)
    psus = recomendar_psu(cpu_info["tdp"], gpu_info["memory"])

    return {
        "cpu": cpu_info,
        "gpu": gpu_info,
        "motherboard_top3": motherboards,
        "ram_top3": ram_options,
        "psu_top3": psus
    }
