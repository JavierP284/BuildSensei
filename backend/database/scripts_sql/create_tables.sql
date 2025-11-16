-- =========================================
-- BuildSensei - Database Schema (Actualizado)
-- =========================================

PRAGMA foreign_keys = ON;

-- ============================
-- Tabla: CPU
-- ============================
DROP TABLE IF EXISTS cpu;

CREATE TABLE cpu (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    core_count INTEGER,
    core_clock REAL,
    boost_clock REAL,
    microarchitecture TEXT,
    tdp INTEGER,
    graphics TEXT
);

-- ============================
-- Tabla: Motherboard
-- ============================
DROP TABLE IF EXISTS motherboard;

CREATE TABLE motherboard (
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
DROP TABLE IF EXISTS memory;

CREATE TABLE memory (
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
DROP TABLE IF EXISTS video_card;

CREATE TABLE video_card (
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
DROP TABLE IF EXISTS power_supply;

CREATE TABLE power_supply (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL,
    efficiency TEXT,
    wattage INTEGER,
    modular TEXT
);
