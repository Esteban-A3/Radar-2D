# Radar-2D - Interfaz Gráfica (GUI) 🖥️📡

Este módulo contiene la interfaz gráfica del proyecto **Radar-2D**, desarrollada en **Python** utilizando **Tkinter**. Su función es visualizar en tiempo real los datos obtenidos desde el sistema de radar basado en Arduino, mostrando el barrido del sensor, la posición de los objetos detectados y diferentes indicadores visuales.

---

## 📂 Contenido de la Rama

| Archivo | Descripción |
|----------|------------|
| `GUI_Radar.py` | Aplicación principal de la interfaz gráfica. Procesa los datos recibidos por el puerto serial y representa visualmente el radar en tiempo real. |
| `radar_gui.py` | Versión alternativa o experimental de la interfaz utilizada durante el desarrollo del proyecto. |
| `leer_radar.py` | Herramienta de prueba para verificar la recepción correcta de datos desde Arduino mediante comunicación serial. |
| `README.md` | Documentación de la rama. |

---

## ✨ Características

### 📡 Visualización en Tiempo Real

- Representación gráfica del barrido entre **0° y 180°**.
- Actualización continua de los datos recibidos desde Arduino.
- Movimiento sincronizado con el servomotor.

### 🎯 Detección de Objetos

- Muestra la ubicación de obstáculos detectados.
- Conversión automática de ángulo y distancia a coordenadas 2D.
- Actualización dinámica de los puntos detectados.

### ⚠️ Sistema de Alertas

- Indicadores visuales cuando un objeto entra dentro del rango de detección definido.
- Retroalimentación inmediata para el usuario.

### 🖥️ Interfaz Intuitiva

- Construida completamente con **Tkinter**.
- Uso del componente **Canvas** para el renderizado gráfico.
- Diseño ligero y fácil de ejecutar en cualquier equipo con Python.

---

## 🛠️ Requisitos

- Python 3.x
- Tkinter (incluido por defecto en la mayoría de instalaciones de Python)
- PySerial

Instalar PySerial:

```bash
pip install pyserial
```

---

## 🚀 Ejecución

### 1. Verificar la comunicación serial

Antes de abrir la interfaz gráfica, se recomienda comprobar que Arduino está enviando datos correctamente:

```bash
python leer_radar.py
```

Si los datos se muestran correctamente en la terminal, la comunicación está funcionando.

### 2. Iniciar la interfaz gráfica

```bash
python GUI_Radar.py
```

La ventana mostrará el radar en funcionamiento y actualizará la información recibida desde Arduino en tiempo real.

---

## 🔗 Relación con el Proyecto

Esta rama forma parte del proyecto **Radar-2D**, integrando la comunicación serial proveniente del microcontrolador Arduino con una representación gráfica interactiva que permite visualizar el entorno detectado por el sensor.

---

## 📸 Funcionalidades Principales

- Barrido de radar de **0° a 180°**.
- Detección de obstáculos en tiempo real.
- Comunicación serial con Arduino.
- Interfaz desarrollada en **Python + Tkinter**.
- Representación gráfica dinámica de los objetos detectados.

---

## 👨‍💻 Autor

Proyecto desarrollado como parte de un sistema de radar 2D basado en Arduino y Python para la visualización y detección de objetos en tiempo real.
