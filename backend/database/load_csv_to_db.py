import sqlite3
import pandas as pd
import os

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "buildsensei.db")
DATASET_PATH = os.path.join(os.path.dirname(BASE_DIR), "datasets")

# Dataset → columnas a usar para cada tabla
TABLE_SPECS = {
    "cpu": {
        "file": "cpu.csv",
        "columns": ["name", "price", "tdp", "graphics", "core_count", "core_clock", "boost_clock"]
    },
    "motherboard": {
        "file": "motherboard.csv",
        "columns": ["name", "price", "socket", "form_factor", "max_memory", "memory_slots"]
    },
    "memory": {
        "file": "memory.csv",
        "columns": ["name", "price", "speed", "modules", "cas_latency"]
    },
    "video_card": {
        "file": "video-card.csv",
        "columns": ["name", "price", "chipset", "memory", "length"]
    },
    "power_supply": {
        "file": "power-supply.csv",
        "columns": ["name", "price", "efficiency", "wattage", "modular"]
    }
}

def clean_dataframe(df, columns):
    """Keep only required columns, drop missing columns gracefully."""
    available_cols = [col for col in columns if col in df.columns]
    return df[available_cols].copy()

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("\n=== BuildSensei CSV → SQLite Loader ===\n")

    for table, info in TABLE_SPECS.items():
        csv_path = os.path.join(DATASET_PATH, info["file"])

        print(f"→ Loading {csv_path} into {table}...")

        # Read CSV
        df = pd.read_csv(csv_path)

        # Clean dataframe
        df = clean_dataframe(df, info["columns"])

        # Replace NaN with None
        df = df.where(pd.notnull(df), None)

        # Insert into SQL
        placeholders = ", ".join(["?"] * len(df.columns))
        columns_sql = ", ".join(df.columns)

        insert_query = f"INSERT INTO {table} ({columns_sql}) VALUES ({placeholders})"

        cursor.executemany(insert_query, df.values.tolist())
        conn.commit()

        print(f"   ✔ Inserted {len(df)} records into {table}")

    conn.close()
    print("\n=== DONE! Database is ready. ===\n")


if __name__ == "__main__":
    main()
