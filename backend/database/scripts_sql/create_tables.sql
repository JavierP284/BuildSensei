-- =========================================
-- BuildSensei - Database Schema
-- Tablas basadas en los campos seleccionados
-- =========================================

PRAGMA foreign_keys = ON;

-- ============================
-- Tabla: CPU
-- ============================
CREATE TABLE IF NOT EXISTS cpu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    tdp INTEGER,
    graphics TEXT,
    core_count INTEGER,
    core_clock REAL,
    boost_clock REAL
);

-- ============================
-- Tabla: Motherboard
-- ============================
CREATE TABLE IF NOT EXISTS motherboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    socket TEXT NOT NULL,
    form_factor TEXT,
    max_memory INTEGER,
    memory_slots INTEGER
);

-- ============================
-- Tabla: RAM
-- ============================
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    speed INTEGER,
    modules TEXT,
    cas_latency REAL
);

-- ============================
-- Tabla: GPU
-- ============================
CREATE TABLE IF NOT EXISTS video_card (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    chipset TEXT,
    memory INTEGER,
    length REAL
);

-- ============================
-- Tabla: Power Supply (PSU)
-- ============================
CREATE TABLE IF NOT EXISTS power_supply (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    efficiency TEXT,
    wattage INTEGER,
    modular TEXT
);
