# BuildSensei

BuildSensei es un sistema experto diseñado para eliminar la incertidumbre al armar una computadora. Mediante reglas de compatibilidad y modelos de balanceo, garantiza que cada componente seleccionado sea 100% compatible y además esté óptimamente equilibrado para el rendimiento que buscas.

![Logo](frontend/img/Logo2.png)

---

## 🚀 Descripción General

BuildSensei funciona como un asistente inteligente para armar tu PC.  
El sistema evalúa compatibilidades reales entre CPU, GPU, RAM, motherboard y PSU, asegurando que la configuración final no solo funcione, sino que esté equilibrada para evitar cuellos de botella.

---

## 🔧 Características

- **Selección de Componentes:** Elige entre una base de datos de CPUs, GPUs, motherboards, fuentes de poder y memoria RAM.
- **Verificación de Compatibilidad:** El sistema experto valida compatibilidad eléctrica, de chipset, conectores y requerimientos mínimos.
- **Balanceo de Rendimiento:** Recomienda ajustes si alguna pieza genera cuello de botella.
- **Interfaz Intuitiva:** Frontend sencillo y directo para seleccionar los componentes.
- **API de Compatibilidad:** Endpoint dedicado para validar compatibilidad entre piezas.

---

## 🧰 Tecnologías Utilizadas

### Backend
- Python  
- Flask  
- SQLite  

### Frontend
- HTML  
- CSS  
- JavaScript  

---

## 📦 Instalación

Sigue estos pasos para ejecutar BuildSensei en tu entorno local.

### Prerrequisitos
Se encuentran en requirements.txt
- Flask==3.0.3
- Flask-Cors==4.0.0
- pandas==2.2.3
- sqlite3-binary==2.6.0
- Werkzeug==3.0.1

### 1. Clonar el repositorio
```sh
git clone https://github.com/tu-usuario/buildsensei.git
cd buildsensei
