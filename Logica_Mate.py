import math


def polar_a_cartesiano(r: float, theta_grados: float) -> tuple[float, float]:
    """
    Convierte una coordenada polar (r, θ) a cartesiana (x, y).
    math.cos/sen trabajan en radianes, por eso se usa
    math.radians() para convertir desde grados.
    """
    theta_rad = math.radians(theta_grados)
    x = r * math.cos(theta_rad)
    y = r * math.sin(theta_rad)
    return x, y


def cartesiano_a_polar(x: float, y: float) -> tuple[float, float]:
    """
    Conversión inversa: de (x, y) a (r, θ).
    Útil para depuración y para validar la conversión directa.
    """
    r = math.hypot(x, y)                       # √(x² + y²)
    theta_grados = math.degrees(math.atan2(y, x))
    return r, theta_grados

def calcular_velocidad(x1: float, y1: float, t1: float,
                        x2: float, y2: float, t2: float) -> dict:
    """
    Calcula la velocidad de un objeto entre dos lecturas.
    Si delta_t es 0 o negativo (lecturas duplicadas o desordenadas),
    retorna velocidad 0 para evitar división por cero.
    """
    delta_t = t2 - t1

    if delta_t <= 0:
        return {"velocidad": 0.0, "vx": 0.0, "vy": 0.0, "delta_t": 0.0}

    delta_x = x2 - x1
    delta_y = y2 - y1

    vx = delta_x / delta_t
    vy = delta_y / delta_t

    # Magnitud de la velocidad (teorema de Pitágoras)
    distancia_recorrida = math.hypot(delta_x, delta_y)
    velocidad = distancia_recorrida / delta_t

    return {
        "velocidad": velocidad,
        "vx": vx,
        "vy": vy,
        "delta_t": delta_t
    }
