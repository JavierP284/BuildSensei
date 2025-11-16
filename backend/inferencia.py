import sqlite3
from typing import Any, Dict, List, Optional

class ExpertInference:
    def __init__(self, db_path: str = "backend/database/buildsensei.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()

    # ============================================================
    # Helper methods
    # ============================================================
    def _get_component(self, table: str, name: str, fields: List[str]) -> Optional[Dict[str, Any]]:
        """Método genérico para obtener un componente de la base de datos."""
        query = f"SELECT {', '.join(fields)} FROM {table} WHERE name = ?"
        row = self.cursor.execute(query, (name,)).fetchone()
        if not row:
            return None
        return dict(zip(fields, row))

    def get_cpu(self, cpu_name: str) -> Optional[Dict[str, Any]]:
        return self._get_component("cpu", cpu_name, ["name", "socket", "tdp"])

    def get_gpu(self, gpu_name: str) -> Optional[Dict[str, Any]]:
        return self._get_component("gpu", gpu_name, ["name", "power"])

    # ============================================================
    # Rules
    # ============================================================

    # -------- Rule 1: Motherboard compatible con CPU --------
    def recommend_motherboards(self, socket: str) -> List[Dict[str, Any]]:
        q = """
        SELECT name, price, chipset, ram_type
        FROM motherboard
        WHERE socket = ?
        ORDER BY price ASC
        LIMIT 3;
        """
        rows = self.cursor.execute(q, (socket,)).fetchall()
        return [{"name": r[0], "price": r[1], "chipset": r[2], "ram_type": r[3]} for r in rows]

    # -------- Rule 2: RAM basada en tipo soportado --------
    def recommend_ram(self, ram_type: str) -> List[Dict[str, Any]]:
        q = """
        SELECT name, size_gb, speed_mhz, price
        FROM ram
        WHERE type = ?
        AND size_gb >= 16
        ORDER BY price ASC
        LIMIT 3;
        """
        rows = self.cursor.execute(q, (ram_type,)).fetchall()
        return [{"name": r[0], "size": r[1], "speed": r[2], "price": r[3]} for r in rows]

    # -------- Rule 3: PSU basada en consumo total --------
    def recommend_psu(self, cpu_tdp: int, gpu_power: int) -> Dict[str, Any]:
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
    def infer(self, cpu_name: str, gpu_name: str) -> Dict[str, Any]:
        try:
            cpu = self.get_cpu(cpu_name)
            if not cpu:
                raise ValueError(f"CPU no encontrada: {cpu_name}")

            gpu = self.get_gpu(gpu_name)
            if not gpu:
                raise ValueError(f"GPU no encontrada: {gpu_name}")
        except ValueError as e:
            return {"error": str(e)}

        # 1) Motherboards compatibles
        motherboards = self.recommend_motherboards(cpu["socket"])

        if not motherboards:
            return {"error": "No se encontraron motherboards compatibles."}

        # 2) RAM para cada motherboard recomendada
        for mb in motherboards:
            mb["recommended_ram"] = self.recommend_ram(mb["ram_type"])

        # 3) PSU recomendada
        psu = self.recommend_psu(cpu["tdp"], gpu["power"])

        return {
            "inputs": {"cpu_name": cpu_name, "gpu_name": gpu_name},
            "components": {"cpu": cpu, "gpu": gpu},
            "recommendations": {"motherboards": motherboards, "psu": psu},
        }


# ============================================================
# Standalone test
# ============================================================
if __name__ == "__main__":
    with ExpertInference() as expert:
        resultado = expert.infer(
            cpu_name="AMD Ryzen 7 7800X3D",
            gpu_name="NVIDIA RTX 4070"
        )

        from pprint import pprint
        pprint(resultado)

        print("\n--- Prueba con componente no existente ---")
        error_test = expert.infer(
            cpu_name="CPU Inexistente",
            gpu_name="NVIDIA RTX 4070"
        )
        pprint(error_test)
