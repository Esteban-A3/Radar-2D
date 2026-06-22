# Radar-2D - Lógica Matemática y Cálculos 📐📡

Esta rama contiene los cálculos matemáticos utilizados en el proyecto **Radar-2D** para determinar la **posición**, **trayectoria** y **velocidad** de los objetos detectados por el sistema. Aquí se implementan las operaciones necesarias para transformar los datos obtenidos por el sensor en información útil para la representación y análisis del movimiento.

---

## 📂 Contenido de la Rama

| Archivo | Descripción |
|----------|------------|
| `Logica_Mate.py` | Implementación de los cálculos matemáticos utilizados para determinar la posición y velocidad de los objetos detectados por el radar. |
| `README.md` | Documentación de la rama. |

---

## ✨ Funcionalidades

### 📍 Cálculo de Posición

- Conversión de los datos de distancia y ángulo obtenidos por el sensor.
- Transformación de coordenadas polares a coordenadas cartesianas.
- Determinación de la ubicación del objeto dentro del plano de detección.

### 📈 Cálculo de Trayectoria

- Seguimiento de la posición de un objeto a través del tiempo.
- Estimación de la dirección de movimiento.
- Generación de datos para la representación gráfica de la trayectoria.

### 🚀 Cálculo de Velocidad

- Comparación de posiciones registradas en distintos instantes de tiempo.
- Determinación de la velocidad aproximada del objeto detectado.
- Base matemática para futuras funciones de predicción de movimiento.

---

## 🧮 Fundamento Matemático

El sistema utiliza conceptos de:

- Trigonometría.
- Geometría analítica.
- Conversión de coordenadas polares a cartesianas.
- Cálculo de distancia entre puntos.
- Velocidad como relación entre desplazamiento y tiempo.

Ejemplo de conversión:

```text
x = r · cos(θ)
y = r · sin(θ)
```

Donde:

- `r` es la distancia medida por el sensor.
- `θ` es el ángulo de detección.
- `x` y `y` representan la posición del objeto en el plano cartesiano.

---

## 🛠️ Requisitos

- Python 3.x
- Librerías matemáticas estándar de Python

---

## 🚀 Ejecución

Para ejecutar los cálculos matemáticos:

```bash
python Logica_Mate.py
```

El programa procesará los datos de entrada y calculará la posición, trayectoria y velocidad de los objetos detectados.

---

## 🔗 Relación con el Proyecto

Esta rama constituye el núcleo matemático del proyecto **Radar-2D**, proporcionando los algoritmos necesarios para interpretar los datos obtenidos por el sensor y convertirlos en información útil para la interfaz gráfica y el análisis del movimiento de objetos.

---

## 📸 Funciones Principales

- Conversión de coordenadas polares a cartesianas.
- Cálculo de posición de objetos.
- Determinación de trayectorias.
- Estimación de velocidad.
- Procesamiento matemático de los datos del radar.

---

## 👨‍💻 Autor

Proyecto desarrollado como parte de un sistema de radar 2D basado en Arduino y Python para la detección, visualización y análisis del movimiento de objetos en tiempo real.
