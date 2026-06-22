# Radar-2D - Comunicación Serial 🔌📡

Esta rama contiene los módulos desarrollados para establecer y verificar la comunicación serial entre el sistema **Arduino** y las aplicaciones en **Python** del proyecto Radar-2D. Su objetivo es detectar automáticamente el puerto de conexión, recibir datos del microcontrolador y validar el correcto intercambio de información antes de integrarlos con los demás componentes del sistema.

---

## 📂 Contenido de la Rama

| Archivo | Descripción |
|----------|------------|
| `comunicacion.py` | Implementa la comunicación serial y la recepción de datos enviados por Arduino. |
| `detectar_puerto.py` | Herramienta para detectar automáticamente el puerto serial donde se encuentra conectado el Arduino. |
| `README.md` | Documentación de la rama. |

---

## ✨ Funcionalidades

### 🔍 Detección Automática de Puerto

- Identifica los puertos seriales disponibles en el sistema.
- Facilita la conexión con Arduino sin necesidad de configurar manualmente el puerto.
- Reduce errores durante la inicialización del sistema.

### 🔌 Comunicación Serial

- Establecimiento de conexión entre Python y Arduino.
- Lectura continua de datos enviados por el microcontrolador.
- Manejo de la transmisión de información en tiempo real.

### 🧪 Pruebas de Conectividad

- Verificación del correcto funcionamiento del enlace serial.
- Validación de los datos recibidos.
- Base para la integración con los módulos de visualización y procesamiento matemático.

---

## 🛠️ Requisitos

- Python 3.x
- PySerial

Instalar PySerial:

```bash
pip install pyserial
```

---

## 🚀 Ejecución

### 1. Detectar el Puerto de Arduino

```bash
python detectar_puerto.py
```

El programa mostrará los puertos seriales disponibles y permitirá identificar el puerto utilizado por el Arduino.

### 2. Verificar la Comunicación

```bash
python comunicacion.py
```

Si la conexión es exitosa, se mostrarán en pantalla los datos recibidos desde el microcontrolador.

---

## 🔗 Relación con el Proyecto

Esta rama corresponde a la etapa de desarrollo y pruebas de comunicación del proyecto **Radar-2D**. Los scripts aquí incluidos permitieron validar la conexión serial entre Arduino y Python, sirviendo como base para la integración posterior con los módulos de cálculo matemático y la interfaz gráfica.

---

## 📸 Funciones Principales

- Detección automática de puertos seriales.
- Comunicación entre Arduino y Python.
- Recepción de datos en tiempo real.
- Pruebas de conectividad y depuración.
- Base para la integración de los demás módulos del sistema.

---

## 👥 Integrantes

- **Dominick Rodríguez**
- **Esteban Sánchez**

---

## 👨‍💻 Autoría

Proyecto desarrollado por **Dominick Rodríguez** y **Esteban Sánchez** como parte del sistema **Radar-2D**, integrando Arduino y Python para la detección, procesamiento y visualización de objetos en tiempo real.
