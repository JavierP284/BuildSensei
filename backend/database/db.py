import sqlite3
import os

# ================================
#  Database Connection Helper
# ================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "buildsensei.db")


def get_connection():
    """Return a new SQLite connection."""
    return sqlite3.connect(DB_PATH)


# ================================
#  Generic Query Helpers
# ================================

def fetch_all(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_one(query, params=()):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    row = cursor.fetchone()
    conn.close()
    return row


# ================================
#  CPU Queries
# ================================

def get_all_cpus(limit=None):
    q = "SELECT * FROM cpu"
    if limit:
        q += f" LIMIT {limit}"
    return fetch_all(q)


def get_cpu_by_id(cpu_id):
    return fetch_one("SELECT * FROM cpu WHERE id = ?", (cpu_id,))


def search_cpu(name):
    return fetch_all(
        "SELECT * FROM cpu WHERE name LIKE ?",
        (f"%{name}%",)
    )


# ================================
#  Motherboard Queries
# ================================

def get_all_motherboards(limit=None):
    q = "SELECT * FROM motherboard"
    if limit:
        q += f" LIMIT {limit}"
    return fetch_all(q)


def get_motherboard_by_id(mb_id):
    return fetch_one("SELECT * FROM motherboard WHERE id = ?", (mb_id,))


def get_motherboards_by_socket(socket):
    return fetch_all(
        "SELECT * FROM motherboard WHERE socket = ?",
        (socket,)
    )


# ================================
#  Memory (RAM) Queries
# ================================

def get_all_ram(limit=None):
    q = "SELECT * FROM memory"
    if limit:
        q += f" LIMIT {limit}"
    return fetch_all(q)


def get_ram_by_id(ram_id):
    return fetch_one("SELECT * FROM memory WHERE id = ?", (ram_id,))


# ================================
#  GPU (Video Card) Queries
# ================================

def get_all_gpus(limit=None):
    q = "SELECT * FROM video_card"
    if limit:
        q += f" LIMIT {limit}"
    return fetch_all(q)


def get_gpu_by_id(gpu_id):
    return fetch_one("SELECT * FROM video_card WHERE id = ?", (gpu_id,))


# ================================
#  Power Supply (PSU) Queries
# ================================

def get_all_psu(limit=None):
    q = "SELECT * FROM power_supply"
    if limit:
        q += f" LIMIT {limit}"
    return fetch_all(q)


def get_psu_by_id(psu_id):
    return fetch_one("SELECT * FROM power_supply WHERE id = ?", (psu_id,))


# ================================
#  Compatibility Helpers
# ================================

def get_compatible_motherboards_for_cpu(cpu_id):
    """Return all motherboards with matching socket."""
    cpu = get_cpu_by_id(cpu_id)
    if cpu is None:
        return []

    socket = cpu[3]  # assuming order is id, name, price, socket...
    return get_motherboards_by_socket(socket)


def get_psu_by_min_wattage(min_watts):
    return fetch_all(
        "SELECT * FROM power_supply WHERE wattage >= ?",
        (min_watts,)
    )
