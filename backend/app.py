from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database.db import get_connection
from inferencia import obtener_recomendaciones

app = FastAPI(title="BuildSensei API")

# CORS para permitir frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
#   ENDPOINT: LISTAR CPU
# -----------------------------
@app.get("/cpus")
def listar_cpus():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, core_count, core_clock, boost_clock, microarchitecture, tdp, graphics FROM cpu")
    rows = cursor.fetchall()

    cpus = []
    for r in rows:
        cpus.append({
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "core_count": r[3],
            "core_clock": r[4],
            "boost_clock": r[5],
            "microarchitecture": r[6],
            "tdp": r[7],
            "graphics": r[8]
        })

    conn.close()
    return cpus


# -----------------------------
#   ENDPOINT: LISTAR GPU
# -----------------------------
@app.get("/gpus")
def listar_gpus():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, price, chipset, memory, core_clock, boost_clock, tdp FROM video_card")
    rows = cursor.fetchall()

    gpus = []
    for r in rows:
        gpus.append({
            "id": r[0],
            "name": r[1],
            "price": r[2],
            "chipset": r[3],
            "memory": r[4],
            "core_clock": r[5],
            "boost_clock": r[6],
            "tdp": r[7],
        })

    conn.close()
    return gpus


# -----------------------------
#   ENDPOINT: RECOMENDACIONES
# -----------------------------
@app.get("/recomendar")
def recomendar(cpu_id: int, gpu_id: int):
    """
    Recibe los IDs del CPU y GPU elegidos
    y devuelve:
     - Top 3 motherboards compatibles
     - Top 3 memorias recomendadas
     - Top 3 PSUs recomendadas
    """

    resultado = obtener_recomendaciones(cpu_id, gpu_id)

    return {
        "cpu_id": cpu_id,
        "gpu_id": gpu_id,
        "recomendaciones": resultado
    }
