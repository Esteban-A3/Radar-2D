import math
import time

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

class TrackerObjetos:
    """
    Mantiene el estado de todos los objetos detectados por el radar
    y resuelve la asociación de nuevas lecturas a objetos existentes.
    """

    UMBRAL_ASOCIACION_CM = 15.0   # distancia máxima para considerar "mismo objeto"
    TIMEOUT_SEGUNDOS     = 3.0    # tiempo sin lecturas antes de eliminar el objeto

    def __init__(self):
        # { id_objeto: { "x", "y", "t", "angulo", "distancia", "velocidad", "vx", "vy" } }
        self._objetos: dict[int, dict] = {}
        self._siguiente_id = 1

    def procesar_lectura(self, angulo: float, distancia: float,
                          timestamp: float = None) -> int:
        """
        Procesa una nueva lectura (angulo, distancia) del sensor.
        Decide si pertenece a un objeto existente o crea uno nuevo,
        actualiza su posición, velocidad y timestamp.
        id_objeto — identificador del objeto actualizado o creado
        """
        if timestamp is None:
            timestamp = time.time()

        # Ignorar lecturas fuera de rango (el Arduino envía -1
        # cuando el HC-SR04 no detecta nada, según leer_radar.py)
        if distancia < 0:
            return -1

        x, y = polar_a_cartesiano(distancia, angulo)

        id_objeto = self._buscar_objeto_cercano(x, y)

        if id_objeto is None:
            # No hay ningún objeto activo cerca: crear uno nuevo
            id_objeto = self._siguiente_id
            self._siguiente_id += 1
            self._objetos[id_objeto] = {
                "x": x, "y": y, "t": timestamp,
                "angulo": angulo, "distancia": distancia,
                "velocidad": 0.0, "vx": 0.0, "vy": 0.0
            }
        else:
            # Objeto existente: calcular velocidad con la lectura anterior
            anterior = self._objetos[id_objeto]
            resultado_vel = calcular_velocidad(
                anterior["x"], anterior["y"], anterior["t"],
                x, y, timestamp
            )
            self._objetos[id_objeto] = {
                "x": x, "y": y, "t": timestamp,
                "angulo": angulo, "distancia": distancia,
                "velocidad": resultado_vel["velocidad"],
                "vx": resultado_vel["vx"],
                "vy": resultado_vel["vy"]
            }

        return id_objeto

    def _buscar_objeto_cercano(self, x: float, y: float) -> int | None:
        """
        Busca, entre los objetos activos, el más cercano a (x, y).
        Retorna su ID si está dentro de UMBRAL_ASOCIACION_CM,
        o None si ningún objeto activo califica (lectura nueva).
        """
        mejor_id = None
        mejor_distancia = self.UMBRAL_ASOCIACION_CM

        for id_objeto, datos in self._objetos.items():
            dist = math.hypot(x - datos["x"], y - datos["y"])
            if dist < mejor_distancia:
                mejor_distancia = dist
                mejor_id = id_objeto

        return mejor_id

    def limpiar_objetos_perdidos(self, timestamp: float = None) -> list[int]:
        """
        Elimina objetos que no han recibido lecturas en más de
        TIMEOUT_SEGUNDOS. Debe llamarse periódicamente
        """
        if timestamp is None:
            timestamp = time.time()

        eliminados = []
        for id_objeto, datos in list(self._objetos.items()):
            if timestamp - datos["t"] > self.TIMEOUT_SEGUNDOS:
                del self._objetos[id_objeto]
                eliminados.append(id_objeto)

        return eliminados

    def obtener_objetos_activos(self) -> dict:
        """Retorna una copia del diccionario de objetos activos."""
        return dict(self._objetos)