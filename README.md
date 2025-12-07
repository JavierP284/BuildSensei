# BuildSensei

BuildSensei es un sistema experto diseñado para eliminar la incertidumbre al armar una computadora. Mediante reglas de compatibilidad y modelos de balanceo, garantiza que cada componente seleccionado sea 100% compatible y además esté óptimamente equilibrado para el rendimiento que buscas.

![Logo](frontend/img/Logo2.png)

---

## ¿Qué hace?

- Comprueba que CPU, GPU, placa, memoria y fuente funcionen juntos.
- Advierte si hay riesgo de cuello de botella.
- Sugiere si la fuente de poder es suficiente.
- Muestra enlaces de referencia a benchmarks de la GPU (cuando estén disponibles).

---

## ¿Por qué usarlo?

- Evita comprar piezas incompatibles.
- Te da una guía rápida sobre equilibrio rendimiento/energía.
- Ideal para usuarios que quieren armar su PC con confianza sin profundizar en detalles técnicos.

---

## Cómo probarlo localmente (Windows)

1. Clona el repositorio:
```sh
git clone https://github.com/JavierP284/BuildSensei
cd buildsensei
```

2. Instala las dependencias:
```sh
pip install -r requirements.txt
```

3. Ejecuta el servidor:
```sh
python app.py
```

---

## Tecnologías Utilizadas

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
git clone https://github.com/JavierP284/BuildSensei
cd buildsensei
```

### 2. Instalar las dependencias
```sh
pip install -r requirements.txt
```

### 3. Ejecutar el servidor
```sh
python app.py
```
