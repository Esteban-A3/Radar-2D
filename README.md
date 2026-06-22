# Radar-2D - Interfaz Gráfica (GUI) 🖥️

Este módulo contiene la aplicación de interfaz gráfica desarrollada en Python utilizando **Tkinter** para visualizar en tiempo real los datos capturados por el radar Arduino (barrido, distancias y alertas).

---
📂 Contenido de la Rama

| Archivo         | Descripción                                                                                                                                     |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `GUI_Radar.py`  | Aplicación principal de la interfaz gráfica. Procesa los datos recibidos por el puerto serial y representa visualmente el radar en tiempo real. |
| `radar_gui.py`  | Versión alternativa o experimental de la interfaz utilizada durante el desarrollo del proyecto.                                                 |
| `leer_radar.py` | Herramienta de prueba para verificar la recepción correcta de datos desde Arduino mediante comunicación serial.                                 |
| `README.md`     | Documentación de la rama.                                                                                                                       |


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
