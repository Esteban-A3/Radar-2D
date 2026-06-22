# Radar 2D — Sistema de Detección de Objetos

> Proyecto 2 — Fundamentos de Sistemas Computacionales | ITCR | I Semestre 2026

![Arduino](https://img.shields.io/badge/Hardware-Arduino_UNO-00979D?style=flat&logo=arduino)
![Python](https://img.shields.io/badge/Software-Python_3.10+-blue?style=flat&logo=python)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-orange?style=flat)
![PySerial](https://img.shields.io/badge/Serial-PySerial-green?style=flat)
![License](https://img.shields.io/badge/Proyecto-ITCR-red?style=flat)

---

## Descripción

Radar 2D es un sistema de detección de objetos en tiempo real que combina hardware y software.
Un sensor ultrasónico HC-SR04 montado sobre un servomotor realiza barridos de 0° a 180°,
enviando los datos al computador vía serial. Una interfaz gráfica en Python los procesa,
muestra los objetos detectados en un HUD estilo radar militar y calcula su velocidad y
trayectoria futura.

---

## Estructura del main

```
Radar-2D/
│
├── radar_2d.py                        # Código principal — GUI, tracker y lógica completa
├── radar_final_v2.ino                 # Firmware Arduino — barrido servo + sensor HC-SR04
│
└── archivos_adicionales/              # Documentación y diagramas
    ├── Documento_Tecnico_Radar2D.pdf          # Documento técnico del proyecto
    ├── Radar2D_Documento_de_Atributos.pdf     # Documento acreditación CI
    ├── Figura1_Arquitectura.png               # Diagrama de arquitectura del sistema
    ├── Figura2_Modulos.png                    # Diagrama de módulos del software
    └── Figura3_Conexiones_Arduino.png         # Diagrama de conexiones físicas
```

---

## Archivos Contenidos

| Archivo | Contenido |
|--------|-----------|
| `main` | Código completo y funcional (Python + Arduino) |
| `archivos_adicionales` | Documentación, diagramas y figuras |

---

## Lista de Materiales

| Componente | Cantidad |
|------------|----------|
| Arduino UNO (con cable USB) | 1 |
| Sensor ultrasónico HC-SR04 | 1 |
| Servomotor 180° (SG90 / MG996R) | 1 |
| LED rojo | 1 |
| Resistencia 220Ω | 1 |
| Cables de conexión | ~10 |

---

## Diagrama de Conexiones

| Componente | Pin componente | Pin Arduino |
|------------|---------------|-------------|
| HC-SR04 | VCC | 5V |
| HC-SR04 | GND | GND |
| HC-SR04 | TRIG | D9 |
| HC-SR04 | ECHO | D10 |
| Servomotor | VCC (rojo) | 5V |
| Servomotor | GND (marrón) | GND |
| Servomotor | SIG (naranja) | D6 (~PWM) |
| LED rojo | Ánodo (+) | D13 → R220Ω |
| LED rojo | Cátodo (−) | GND |

> Ver diagrama completo: [`archivos_adicionales/Figura3_Conexiones_Arduino.png`](archivos_adicionales/Figura3_Conexiones_Arduino.png)

---

## Instalación y Ejecución

### Requisitos

```bash
Python 3.10+
pip install pyserial pillow
```

### Pasos

1. Subí el firmware al Arduino:
   - Abrí `radar_final_v2.ino` en el IDE de Arduino
   - Seleccioná la placa y el puerto correcto
   - Subí el sketch y **cerrá el IDE** antes de correr el Python

2. Ejecutá la interfaz:

```bash
python radar_2d.py
```

3. En el menú, seleccioná el puerto COM del Arduino y presioná **CONECTAR**.

> ⚠️ El IDE de Arduino y el script de Python no pueden usar el mismo puerto serial al mismo tiempo.

---

## Funcionalidades del Sistema

### Hardware (Arduino)
- Barrido continuo de **0° a 180°** en pasos de 2°, ida y vuelta
- Transmisión de datos por serial en formato `"ángulo,distancia"` a 9600 baudios
- **LED rojo intermitente** de alerta montado sobre el sensor
- Timeout de lectura para descartar ecos inválidos

### Software (Python / Tkinter)
| Función | Descripción |
|---------|-------------|
| Posición en tiempo real | Conversión polar → cartesiana y representación en canvas radar |
| Velocidad del objeto | Cálculo usando `v = d/t` entre lecturas consecutivas |
| Tracker multi-objeto | Asociación por distancia euclidiana mínima con umbral de 15 cm |
| Predicción de trayectoria | Movimiento parabólico: `y(t) = y₀ + vy·t + 0.5·g·t²` |
| Detección automática | Escaneo automático del puerto COM del Arduino al iniciar |
| Lectura no bloqueante | Hilo daemon + `queue.Queue` para no congelar la GUI |

---

## Arquitectura del Sistema

```
[HC-SR04]──┐
           ├──► [Arduino UNO] ──USB Serial──► [LectorSerial (hilo)] ──Queue──► [RadarGUI]
[Servo]────┘                                        │
[LED]──────────────────────────────────────    [Tracker + Matemáticas]
```

> Ver diagramas detallados en [`archivos_adicionales/`](archivos_adicionales/)

---

## Capturas del Sistema

> *(Agregar fotos de la maqueta y la GUI aquí)*

---

## Documentación

| Documento | Descripción |
|-----------|-------------|
| [Documento Técnico](archivos_adicionales/Documento_Tecnico_Radar2D.pdf) | Conclusiones, análisis de resultados, bibliotecas y diagramas |
| [Acreditación CI](archivos_adicionales/Radar2D_Documento_de_Atributos.pdf) | Identificación de problemas técnicos y planteamiento de soluciones |

---

## Autores

**Esteban Alejandro Sánchez Ledezma** — ITCR, Fundamentos de Sistemas Computacionales, 2026  
**Dominick Robles** — ITCR, Fundamentos de Sistemas Computacionales, 2026

> Profesor: Leonardo Andrés Araya Martínez
