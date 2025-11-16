import sqlite3

class ExpertInference:
    def __init__(self, db_path="backend/database/buildsensei.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    # ============================================================
    # Helper methods
    # ============================================================
    def get_cpu(self, cpu_name):
        q = "SELECT name, socket, tdp FROM cpu WHERE name = ?"
        row = self.cursor.execute(q, (cpu_name,)).fetchone()
        if not row:
            raise ValueError("CPU no encontrada")
        return {"name": row[0], "socket": row[1], "tdp": row[2]}

    def get_gpu(self, gpu_name):
        q = "SELECT name, power FROM gpu WHERE name = ?"
        row = self.cursor.execute(q, (gpu_name,)).fetchone()
        if not row:
            raise ValueError("GPU no encontrada")
        return {"name": row[0], "power": row[1]}

    # ============================================================
    # Rules
    # ============================================================

    # -------- Rule 1: Motherboard compatible con CPU --------
    def recommend_motherboards(self, socket):
        q = """
        SELECT name, price, chipset
        FROM motherboard
        WHERE socket = ?
        ORDER BY price ASC
        LIMIT 3;
        """
        rows = self.cursor.execute(q, (socket,)).fetchall()
        return [{"name": r[0], "price": r[1], "chipset": r[2]} for r in rows]

    # -------- Rule 2: RAM basada en tipo soportado por la motherboard --------
    def get_mb_ram_type(self, motherboard_name):
        q = "SELECT ram_type FROM motherboard WHERE name = ?"
        row = self.cursor.execute(q, (motherboard_name,)).fetchone()
        return row[0] if row else None

    def recommend_ram(self, ram_type):
        q = """
        SELECT name, size_gb, speed_mhz, price
        FROM ram
        WHERE type = ?
        ORDER BY price ASC
        LIMIT 3;
        """
        rows = self.cursor.execute(q, (ram_type,)).fetchall()
        return [{"name": r[0], "size": r[1], "speed": r[2], "price": r[3]} for r in rows]

    # -------- Rule 3: PSU basada en consumo GPU + CPU + margen --------
    def recommend_psu(self, cpu_tdp, gpu_power):
        consumo = cpu_tdp + gpu_power
        recomendado = int(consumo * 1.3)  # margen del 30%

        q = """
        SELECT name, wattage, price, modular
        FROM psu
        WHERE wattage >= ?
        ORDER BY wattage ASC
        LIMIT 3;
        """
        rows = self.cursor.execute(q, (recomendado,)).fetchall()

        return {
            "consumo_estimado": consumo,
            "recomendado_minimo": recomendado,
            "psu_top3": [
                {"name": r[0], "wattage": r[1], "price": r[2], "modular": r[3]}
                for r in rows
            ]
        }

    # ============================================================
    # Full inference process
    # ============================================================
    def infer(self, cpu_name, gpu_name):
        cpu = self.get_cpu(cpu_name)
        gpu = self.get_gpu(gpu_name)

        # 1) Motherboards compatibles
        motherboards = self.recommend_motherboards(cpu["socket"])

        # Si no hay motherboards, terminamos
        if not motherboards:
            return {"error": "No se encontraron motherboards compatibles."}

        # Tomamos la primera motherboard como referencia para RAM
        mb_ram_type = self.get_mb_ram_type(motherboards[0]["name"])
        ram = self.recommend_ram(mb_ram_type)

        # 3) PSU recomendada
        psu = self.recommend_psu(cpu["tdp"], gpu["power"])

        return {
            "cpu": cpu,
            "gpu": gpu,
            "motherboards_top3": motherboards,
            "ram_top3": ram,
            "psu_recommendations": psu
        }


# ============================================================
# Standalone test
# ============================================================
if __name__ == "__main__":
    expert = ExpertInference()

    resultado = expert.infer(
        cpu_name="AMD Ryzen 7 7800X3D",
        gpu_name="NVIDIA RTX 4070"
    )

    from pprint import pprint
    pprint(resultado)
