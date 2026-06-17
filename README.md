# Radar-2D - Interfaz Gráfica (GUI) 🖥️

Este módulo contiene la aplicación de interfaz gráfica desarrollada en Python utilizando **Tkinter** para visualizar en tiempo real los datos capturados por el radar Arduino (barrido, distancias y alertas).

---

## 📂 Contenido de esta Rama

* **`GUI_Radar.py`**: Script principal en Python que genera la interfaz gráfica con **Tkinter**, maneja la animación del radar en el Canvas y procesa el feedback visual de las acciones.
* **`leer_radar.py`**: Script de prueba (test) independiente para verificar y asegurar que los datos del puerto serial se están recibiendo y leyendo correctamente desde el Arduino.


---

## 🛠️ Características de la Interfaz

La GUI está diseñada con Tkinter para ofrecer una representación visual limpia y fluida del radar:
* **Animación en Tiempo Real:** Renderizado del barrido de 0 a 180 grados utilizando el componente Canvas, sincronizado con el movimiento del servomotor.
* **Feedback de Acciones:** Indicadores visuales automáticos en la interfaz cuando el sensor detecta un obstáculo dentro del rango de alerta.
* **Mapeo 2D:** Conversión de los datos de ángulo y distancia para dibujarlos dinámicamente en una pantalla bidimensional.

---

## 🚀 Requisitos e Instalación

1. Asegúrate de tener instalado **Python 3.x** (Tkinter viene incluido por defecto en la mayoría de las instalaciones de Python).
2. Instala la librería para la comunicación serial:
   ```bash
   pip install pyserial
3. Prueba de conexión: Antes de lanzar la interfaz completa, ejecuta el script de test para confirmar que hay comunicación con el Arduino:
   ```bash
   python leer_radar.py
4. Una vez verificada la lectura serial, inicia la aplicación principal:
   ```bash
   python GUI_Radar.py
