import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageEnhance
import os
import math
import time
import threading
import queue
import serial
import serial.tools.list_ports


#constantes de color

COLOR_BG         = "#000000"   # negro puro
COLOR_GREEN      = "#00FF46"   # verde radar
COLOR_GREEN_MID  = "#00CC38"   # verde medio
COLOR_GREEN_DIM  = "#00994A"   # verde apagado
COLOR_GREEN_DARK = "#006628"   # verde oscuro
COLOR_HUD_FILL   = "#000D04"   # negro verdoso
COLOR_RED_ALERT  = "#FF2222"   # rojo
COLOR_SCANLINE   = "#001A08"   # verde muy oscuro

FONT_FAMILY = "Courier"
WINDOW_W = 900     # tamaño de la ventana del menú principal
WINDOW_H = 620

# Ruta relativa a la imagen de fondo del menú
BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "radar.png")


#logica matematica 

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


GRAVEDAD_CM_S2 = 50.0   # aceleración constante en cm/s² (ajustable)

def predecir_trayectoria(x0: float, y0: float, vx: float, vy: float,
                          n_puntos: int = 15, dt: float = 0.15,
                          g: float = GRAVEDAD_CM_S2) -> list[tuple[float, float]]:
    """
    Genera una lista de puntos futuros siguiendo una trayectoria
    parabólica simple, a partir de la posición y velocidad actuales.

    Nota sobre el signo de g: en este sistema de coordenadas,
    "y" positivo se aleja del sensor en el sentido de la rejilla
    angular. Se suma 0.5*g*t² para que la
    curva se doble, simulando una parábola.
    """
    puntos = []
    for i in range(n_puntos):
        t = i * dt
        x = x0 + vx * t
        y = y0 + vy * t + 0.5 * g * t ** 2
        puntos.append((x, y))
    return puntos

#Detección de puerto serial del Arduino

def listar_puertos_disponibles() -> list:
    """
    Retorna todos los puertos seriales detectados por el sistema
    operativo, sin filtrar. Útil para depuración y para mostrar
    al usuario qué se detectó si la búsqueda automática falla.
    """
    return list(serial.tools.list_ports.comports())

PALABRAS_CLAVE_ARDUINO = [
    "arduino",      # Arduino oficial (Uno, Nano, Mega genuinos)
    "ch340",        # Clon chino muy común (chip USB-Serial CH340)
    "ch341",        # Variante del CH340
    "usb-serial",   # Descripción genérica de muchos clones
    "usb serial",
    "wch.cn",       # Fabricante del chip CH340
    "ftdi",         # Otro chip USB-Serial común en placas Arduino
]


def detectar_puerto_arduino() -> str | None:
    """
    Busca entre los puertos disponibles uno que parezca ser un
    Arduino, comparando su descripción y fabricante contra.
    """
    puertos = listar_puertos_disponibles()

    for puerto in puertos:
        texto_busqueda = f"{puerto.description} {puerto.manufacturer or ''}".lower()

        for palabra_clave in PALABRAS_CLAVE_ARDUINO:
            if palabra_clave in texto_busqueda:
                return puerto.device

    return None


def detectar_puerto_arduino_detallado() -> dict:
    """
    Versión extendida de detectar_puerto_arduino() que además
    retorna información de diagnóstico, útil para mostrar mensajes
    claros en la GUI cuando la detección falla.
    """
    puertos = listar_puertos_disponibles()
    puerto_arduino = detectar_puerto_arduino()

    return {
        "puerto": puerto_arduino,
        "encontrado": puerto_arduino is not None,
        "puertos_totales": len(puertos),
        "descripciones": [f"{p.device} — {p.description}" for p in puertos]
    }


def conectar_arduino(puerto: str, baudios: int = 9600):
    """
    Intenta abrir la conexión serial con el Arduino.
    """
    try:
        conexion = serial.Serial(puerto, baudios, timeout=1)
        print(f"[Serial] Conectado a {puerto} a {baudios} baudios.")
        # El Arduino se reinicia al abrir el puerto; esperar
        # a que termine el bootloader antes de leer datos.
        time.sleep(2)
        return conexion
    except serial.SerialException as error:
        print(f"[Serial] No se pudo conectar a {puerto}.")
        print(f"[Serial] Detalle del error: {error}")
        return None


def parsear_linea(linea: str):
    """
    Convierte una línea 'angulo,distancia' en (angulo, distancia).
    """
    partes = linea.strip().split(",")

    if len(partes) != 2:
        return None

    try:
        angulo = int(partes[0])
        distancia = int(partes[1])
        return angulo, distancia
    except ValueError:
        return None

class LectorSerial:
    """
    Lee el puerto serial en un hilo de fondo y coloca las
    lecturas (angulo, distancia, timestamp) en una cola
    thread-safe que la GUI consume periódicamente.
    """

    def __init__(self, puerto: str, baudios: int = 9600):
        self.puerto = puerto
        self.baudios = baudios
        self.conexion = None

        self.cola_lecturas: queue.Queue = queue.Queue()

        self._hilo: threading.Thread | None = None
        self._detener_flag = threading.Event()

    def iniciar(self) -> bool:
        """
        Abre la conexión serial y arranca el hilo de lectura.
        """
        self.conexion = conectar_arduino(self.puerto, self.baudios)

        if self.conexion is None:
            return False

        self._detener_flag.clear()
        self._hilo = threading.Thread(
            target=self._loop_lectura,
            daemon=True   # el hilo muere automáticamente si se cierra la app
        )
        self._hilo.start()
        return True

    def _loop_lectura(self):
        """
        Cuerpo del hilo de fondo. Lee líneas del puerto serial
        de forma bloqueante (readline) sin afectar la GUI, ya
        que corre en su propio hilo.
        """
        while not self._detener_flag.is_set():
            try:
                linea_cruda = self.conexion.readline().decode(
                    "utf-8", errors="ignore"
                )

                if not linea_cruda:
                    continue  # timeout sin datos, seguir esperando

                datos = parsear_linea(linea_cruda)

                if datos is None:
                    continue  # línea con formato inesperado, se descarta

                angulo, distancia = datos
                timestamp = time.time()

                self.cola_lecturas.put_nowait((angulo, distancia, timestamp))

            except serial.SerialException:
                print("[Serial] Conexión perdida con el Arduino.")
                break
            except Exception as error:
                print(f"[Serial] Error inesperado en el hilo de lectura: {error}")
                continue

    def detener(self):
        """
        Detiene el hilo de lectura y cierra el puerto serial.
        Debe llamarse al cerrar la ventana del radar.
        """
        self._detener_flag.set()
        if self._hilo is not None:
            self._hilo.join(timeout=2)
        if self.conexion is not None:
            self.conexion.close()
            print("[Serial] Puerto serial cerrado correctamente.")

    def obtener_lecturas_pendientes(self) -> list[tuple[int, int, float]]:
        """
        Extrae todas las lecturas acumuladas en la cola sin bloquear.
        """
        lecturas = []
        while True:
            try:
                lecturas.append(self.cola_lecturas.get_nowait())
            except queue.Empty:
                break
        return lecturas


# Ventana del radar y animación del barrido


# Constantes propias de la ventana del radar
# (COLOR_BG, COLOR_GREEN, etc. ya están definidas en el bloque
#  compartido al inicio del archivo unificado; aquí solo van
#  las que son exclusivas de esta pantalla)
COLOR_SWEEP      = "#00FF46"   # línea de barrido 
COLOR_SWEEP_FADE = "#003318"   # estela del barrido
COLOR_OBJECT     = "#00FF46"   # punto de objeto detectado
COLOR_PREDICT    = "#FF6600"   # línea de predicción parabólica
COLOR_RING       = "#003D1A"   # anillos de distancia 
COLOR_GRID       = "#002210"   # líneas de la rejilla angular

RADAR_WIN_W = 1000
RADAR_WIN_H = 700

class RadarGUI(tk.Toplevel):
    """
    Ventana principal del radar.
    Se abre como Toplevel sobre el menú principal.
    """
    # Centro del círculo radar en el canvas
    RADAR_CX = 360
    RADAR_CY = 340
    RADAR_R  = 280        # radio máximo en píxeles
    RADAR_MAX_DIST = 200  # distancia máxima en cm que representa el radio

    # Ancho del panel lateral de información
    PANEL_X  = 720        # x donde empieza el panel lateral

    def __init__(self, master=None, puerto: str = None, baudios: int = 9600):
        """
        Inicializa la ventana, dibuja el fondo y la rejilla del radar, y arranca el hilo de lectura serial.
        """
        super().__init__(master)
        self.configurar_ventana()
        self.cargar_fuentes()
        self.crear_canvas()
        self.dibujar_fondo_base()
        self.dibujar_anillos()
        self.dibujar_rejilla_angular()
        self.dibujar_etiquetas_angulo()
        self.dibujar_etiquetas_distancia()
        self.dibujar_panel_lateral()
        self.iniciar_barrido()
        self.inicializar_objetos()
        self.conectar_datos_reales(puerto, baudios)

    def configurar_ventana(self):
        self.title("RADAR 2D — ESCANEO ACTIVO")
        self.geometry(f"{RADAR_WIN_W}x{RADAR_WIN_H}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - RADAR_WIN_W) // 2
        y = (self.winfo_screenheight() - RADAR_WIN_H) // 2
        self.geometry(f"{RADAR_WIN_W}x{RADAR_WIN_H}+{x}+{y}")

    def cargar_fuentes(self):
        self.f_tag      = tkfont.Font(family=FONT_FAMILY, size=8)
        self.f_label    = tkfont.Font(family=FONT_FAMILY, size=9)
        self.f_titulo   = tkfont.Font(family=FONT_FAMILY, size=11, weight="bold")
        self.f_dato     = tkfont.Font(family=FONT_FAMILY, size=10)
        self.f_velocidad= tkfont.Font(family=FONT_FAMILY, size=8)

    def crear_canvas(self):
        self.canvas = tk.Canvas(
            self,
            width=RADAR_WIN_W,
            height=RADAR_WIN_H,
            bg=COLOR_BG,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

    def dibujar_fondo_base(self):
        """
        Dibuja el fondo oscuro del área radar y el separador
        entre el canvas del radar y el panel lateral.
        El círculo negro es la 'pantalla' del radar.
        """
        # Fondo general con scanlines
        for y in range(0, RADAR_WIN_H, 4):
            self.canvas.create_line(
                0, y, RADAR_WIN_W, y,
                fill=COLOR_SCANLINE, width=1
            )

        # Círculo base del radar
        cx, cy, r = self.RADAR_CX, self.RADAR_CY, self.RADAR_R
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            fill=COLOR_HUD_FILL,
            outline=COLOR_GREEN,
            width=2
        )

        # Línea vertical separando radar del panel lateral
        self.canvas.create_line(
            self.PANEL_X, 0, self.PANEL_X, RADAR_WIN_H,
            fill=COLOR_GREEN, width=1
        )

        # Header superior
        self.canvas.create_line(
            0, 40, RADAR_WIN_W, 40,
            fill=COLOR_GREEN, width=1
        )
        self.canvas.create_text(
            RADAR_WIN_W // 2, 20,
            anchor="center",
            text="RADAR 2D  //  ESCANEO ACTIVO  //  TEC",
            fill=COLOR_GREEN_DIM,
            font=self.f_tag
        )

        # Punto central del radar
        self.canvas.create_oval(
            cx - 4, cy - 4, cx + 4, cy + 4,
            fill=COLOR_GREEN, outline=""
        )

    NUM_ANILLOS = 4
    
    def dibujar_anillos(self):
            """
            Dibuja NUM_ANILLOS círculos concéntricos equidistantes.
            Cada anillo representa un porcentaje del rango máximo.
            """
            cx, cy, r = self.RADAR_CX, self.RADAR_CY, self.RADAR_R
            for i in range(1, self.NUM_ANILLOS + 1):
                radio = r * i / self.NUM_ANILLOS
                self.canvas.create_oval(
                    cx - radio, cy - radio,
                    cx + radio, cy + radio,
                    outline=COLOR_RING,
                    width=1
                )
    
    def dibujar_rejilla_angular(self):
            """
            Dibuja líneas desde el centro hacia el borde del radar
            cada 30°, formando la rejilla polar.
            Los ángulos van de 0° a 180° (barrido del servo).
            """
            cx, cy, r = self.RADAR_CX, self.RADAR_CY, self.RADAR_R
            for grados in range(0, 181, 30):
                rad = math.radians(grados)
                # Para un radar 2D con barrido de 180°,
                # 0° es la izquierda y 180° la derecha (eje horizontal)
                x = cx + r * math.cos(rad)
                y = cy - r * math.sin(rad)   # y invertida (canvas crece hacia abajo)
                self.canvas.create_line(
                    cx, cy, x, y,
                    fill=COLOR_GRID, width=1
                )

    def dibujar_etiquetas_angulo(self):
            """
            Coloca la etiqueta de grados justo fuera del círculo
            en cada línea de la rejilla (cada 30°).
            """
            cx, cy, r = self.RADAR_CX, self.RADAR_CY, self.RADAR_R
            offset = 16   # píxeles fuera del borde del círculo
    
            for grados in range(0, 181, 30):
                rad = math.radians(grados)
                x = cx + (r + offset) * math.cos(rad)
                y = cy - (r + offset) * math.sin(rad)
                self.canvas.create_text(
                    x, y,
                    text=f"{grados}°",
                    fill=COLOR_GREEN_DIM,
                    font=self.f_tag,
                    anchor="center"
                )
    
    def dibujar_etiquetas_distancia(self):
            """
            Coloca la distancia en cm sobre el eje vertical (90°)
            en cada anillo concéntrico.
            """
            cx, cy, r = self.RADAR_CX, self.RADAR_CY, self.RADAR_R
            for i in range(1, self.NUM_ANILLOS + 1):
                radio   = r * i / self.NUM_ANILLOS
                dist_cm = int(self.RADAR_MAX_DIST * i / self.NUM_ANILLOS)
                # El eje de 90° apunta hacia arriba en el canvas
                y_label = cy - radio + 10
                self.canvas.create_text(
                    cx + 4, y_label,
                    text=f"{dist_cm}cm",
                    fill=COLOR_GREEN_DARK,
                    font=self.f_tag,
                    anchor="w"
                )
    
    def dibujar_panel_lateral(self):
            """
            Panel HUD a la derecha del radar.
            Contiene el título y los slots de información de objetos.
            """
            px = self.PANEL_X + 18
            self.canvas.create_text(
                px, 60,
                anchor="nw",
                text="OBJETOS DETECTADOS",
                fill=COLOR_GREEN,
                font=self.f_titulo
            )
            self.canvas.create_line(
                self.PANEL_X + 10, 82,
                RADAR_WIN_W - 10, 82,
                fill=COLOR_GREEN_DARK, width=1
            )
    
            # Slots para hasta 5 objetos simultáneos
            # Cada slot tiene: ID, ángulo, distancia, velocidad
            self._slots_ids = []    # IDs de canvas de los textos de cada slot
            MAX_OBJETOS = 5
            slot_h = 90             # altura de cada slot en píxeles
    
            for i in range(MAX_OBJETOS):
                y0 = 95 + i * slot_h
    
                # Número de objeto
                self.canvas.create_text(
                    px, y0,
                    anchor="nw",
                    text=f"OBJ-{i+1:02d}",
                    fill=COLOR_GREEN_DARK,
                    font=self.f_tag
                )
    
                # Línea de datos (se actualiza en paso 5)
                id_ang  = self.canvas.create_text(
                    px, y0 + 16,
                    anchor="nw", text="ANG:  ---°",
                    fill=COLOR_GREEN_DIM, font=self.f_dato
                )
                id_dist = self.canvas.create_text(
                    px, y0 + 33,
                    anchor="nw", text="DIST: --- cm",
                    fill=COLOR_GREEN_DIM, font=self.f_dato
                )
                id_vel  = self.canvas.create_text(
                    px, y0 + 50,
                    anchor="nw", text="VEL:  --- cm/s",
                    fill=COLOR_GREEN_MID, font=self.f_dato
                )
    
                # Separador entre slots
                self.canvas.create_line(
                    self.PANEL_X + 10, y0 + 68,
                    RADAR_WIN_W - 10, y0 + 68,
                    fill=COLOR_GREEN_DARK, width=1
                )
    
                self._slots_ids.append({
                    "angulo":    id_ang,
                    "distancia": id_dist,
                    "velocidad": id_vel
                })


    SWEEP_FADE_STEPS = 6    # cuántas líneas de estela
    SWEEP_DELTA      = 2    # grados que avanza por frame en simulación
    SWEEP_INTERVAL   = 30   # ms entre frames (≈33 fps)
    
    def iniciar_barrido(self):
            """
            Inicializa el ángulo de barrido y crea los elementos
            de canvas para la línea y su estela.
            El barrido va de 0° a 180° y vuelve (ping-pong),
            igual que el servo físico.
            """
            self._angulo_actual  = 0.0    # ángulo en grados
            self._direccion      = 1      # +1 = izq→der, -1 = der→izq
    
            # IDs de canvas de la estela (del más antiguo al más reciente)
            self._sweep_estela = []
            for i in range(self.SWEEP_FADE_STEPS):
                linea = self.canvas.create_line(
                    0, 0, 0, 0,
                    fill=COLOR_HUD_FILL,   # invisible al inicio
                    width=2
                )
                self._sweep_estela.append(linea)
    
            # Línea principal del barrido (la más brillante)
            self._sweep_linea = self.canvas.create_line(
                0, 0, 0, 0,
                fill=COLOR_SWEEP,
                width=2
            )
    
            self._animar_barrido()
    
    def _angulo_a_xy(self, grados: float, radio: float):
            """
            Convierte un ángulo en grados a coordenadas (x, y)
            sobre el canvas, dado un radio en píxeles desde el centro del radar.
            """
            rad = math.radians(grados)
            x = self.RADAR_CX + radio * math.cos(rad)
            y = self.RADAR_CY - radio * math.sin(rad)
            return x, y
    
    def _animar_barrido(self):
            """
            Loop de animación de la línea de barrido.
            """
            cx, cy = self.RADAR_CX, self.RADAR_CY
            r      = self.RADAR_R
    
            # Calcular posiciones de la estela (ángulos anteriores)
            for i, linea_id in enumerate(self._sweep_estela):
                # i=0 es la línea más antigua (más apagada)
                offset_grados = (self.SWEEP_FADE_STEPS - i) * self.SWEEP_DELTA * 1.5
                ang_estela = self._angulo_actual - self._direccion * offset_grados
    
                # Oscurecer progresivamente la estela
                intensidad = int(255 * (i + 1) / (self.SWEEP_FADE_STEPS + 1))
                verde_hex  = f"#{0:02x}{intensidad:02x}{0:02x}"
    
                if 0 <= ang_estela <= 180:
                    ex, ey = self._angulo_a_xy(ang_estela, r)
                    self.canvas.coords(linea_id, cx, cy, ex, ey)
                    self.canvas.itemconfig(linea_id, fill=verde_hex)
                else:
                    # Fuera de rango: ocultar esa línea de estela
                    self.canvas.coords(linea_id, cx, cy, cx, cy)
    
            # Dibujar línea principal
            nx, ny = self._angulo_a_xy(self._angulo_actual, r)
            self.canvas.coords(self._sweep_linea, cx, cy, nx, ny)
    
            # Avanzar ángulo (ping-pong entre 0° y 180°)
            self._angulo_actual += self.SWEEP_DELTA * self._direccion
            if self._angulo_actual >= 180:
                self._angulo_actual = 180
                self._direccion = -1
            elif self._angulo_actual <= 0:
                self._angulo_actual = 0
                self._direccion = 1
    
            self.after(self.SWEEP_INTERVAL, self._animar_barrido)
    
    def actualizar_angulo(self, grados: float):
            """
            API para que el hilo serial
            actualice el ángulo de la línea de barrido.
            """
            self._angulo_actual = max(0.0, min(180.0, grados))

    OBJETO_RADIO    = 5      # radio visual del punto de objeto en px
    OBJETO_TIMEOUT  = 3.0    # segundos sin update antes de ocultar el objeto

    def inicializar_objetos(self):
        """
        Prepara el diccionario de objetos activos y sus
        elementos de canvas (punto + etiquetas).
        """
        
        self._objetos = {}

        # Reservar un objeto de canvas por slot para reusarlos
        self._puntos_canvas = {}

        # Arrancar el loop de limpieza de objetos perdidos
        self.limpiar_objetos_perdidos()

    def renderizar_objeto(self, obj_id: int, angulo: float,
                           distancia: float, velocidad: float):
        """
        Dibuja o actualiza la posición de un objeto detectado.
        """
        # Escalar distancia de cm a píxeles
        r_px = (distancia / self.RADAR_MAX_DIST) * self.RADAR_R
        r_px = min(r_px, self.RADAR_R)   # no salir del círculo

        x, y = self._angulo_a_xy(angulo, r_px)

        
        if obj_id not in self._puntos_canvas:
            # Primera vez que aparece este objeto: crear elementos
            punto = self.canvas.create_oval(
                x - self.OBJETO_RADIO, y - self.OBJETO_RADIO,
                x + self.OBJETO_RADIO, y + self.OBJETO_RADIO,
                fill=COLOR_OBJECT, outline=COLOR_GREEN, width=1
            )
            # Cruz de targeting alrededor del punto
            cruz_h = self.canvas.create_line(
                x - 10, y, x + 10, y,
                fill=COLOR_GREEN, width=1
            )
            cruz_v = self.canvas.create_line(
                x, y - 10, x, y + 10,
                fill=COLOR_GREEN, width=1
            )
            self._puntos_canvas[obj_id] = {
                "punto": punto,
                "cruz_h": cruz_h,
                "cruz_v": cruz_v,
            }
        else:
            # Actualizar posición de los elementos existentes
            ids = self._puntos_canvas[obj_id]
            self.canvas.coords(
                ids["punto"],
                x - self.OBJETO_RADIO, y - self.OBJETO_RADIO,
                x + self.OBJETO_RADIO, y + self.OBJETO_RADIO
            )
            self.canvas.coords(ids["cruz_h"], x - 10, y, x + 10, y)
            self.canvas.coords(ids["cruz_v"], x, y - 10, x, y + 10)

       
        self._objetos[obj_id] = {
            "angulo":    angulo,
            "distancia": distancia,
            "velocidad": velocidad,
            "x": x, "y": y,
            "ultimo_update": time.time()
        }

      
        self.actualizar_panel(obj_id)

    def limpiar_objetos_perdidos(self):
        """
        Oculta los objetos que llevan más de OBJETO_TIMEOUT
        segundos sin recibir una nueva lectura.
        """
        ahora = time.time()
        for obj_id, datos in list(self._objetos.items()):
            if ahora - datos["ultimo_update"] > self.OBJETO_TIMEOUT:
                # Ocultar el punto del canvas
                if obj_id in self._puntos_canvas:
                    ids = self._puntos_canvas[obj_id]
                    for key in ids:
                        self.canvas.coords(ids[key], 0, 0, 0, 0)
                del self._objetos[obj_id]
                # Limpiar el slot del panel lateral
                slot_idx = (obj_id - 1) % len(self._slots_ids)
                self.limpiar_slot(slot_idx)

        self.after(500, self.limpiar_objetos_perdidos)

    def actualizar_panel(self, obj_id: int):
        """
        Actualiza el slot del panel lateral con los datos
        actuales del objeto identificado por obj_id.
        """
        if obj_id not in self._objetos:
            return

        datos    = self._objetos[obj_id]
        slot_idx = (obj_id - 1) % len(self._slots_ids)
        slot     = self._slots_ids[slot_idx]

        self.canvas.itemconfig(
            slot["angulo"],
            text=f"ANG:  {datos['angulo']:.1f}°",
            fill=COLOR_GREEN
        )
        self.canvas.itemconfig(
            slot["distancia"],
            text=f"DIST: {datos['distancia']:.1f} cm",
            fill=COLOR_GREEN
        )
        self.canvas.itemconfig(
            slot["velocidad"],
            text=f"VEL:  {datos['velocidad']:.1f} cm/s",
            fill=COLOR_GREEN_MID
        )

    def limpiar_slot(self, slot_idx: int):
        """Resetea un slot del panel lateral a su estado vacío."""
        if slot_idx >= len(self._slots_ids):
            return
        slot = self._slots_ids[slot_idx]
        self.canvas.itemconfig(slot["angulo"],    text="ANG:  ---°",    fill=COLOR_GREEN_DARK)
        self.canvas.itemconfig(slot["distancia"], text="DIST: --- cm",  fill=COLOR_GREEN_DARK)
        self.canvas.itemconfig(slot["velocidad"], text="VEL:  --- cm/s",fill=COLOR_GREEN_DARK)


    # predicción de trayectoria futura

    #  Usa predecir_trayectoria() de matematicas.py para calcular
    #  los puntos futuros y los dibuja como una línea punteada
    #  saliendo del objeto.

    def dibujar_trayectoria(self, obj_id: int, vx_cms: float, vy_cms: float):
        """
        Dibuja la trayectoria parabólica predicha para un objeto.

        Params:
            obj_id   — ID del objeto
            vx_cms   — componente X de velocidad en cm/s
            vy_cms   — componente Y de velocidad en cm/s
        """
        if obj_id not in self._objetos:
            return

        datos  = self._objetos[obj_id]
        x0, y0 = datos["x"], datos["y"]
        escala = self.RADAR_R / self.RADAR_MAX_DIST   # px por cm

        # Velocidades en px/s
        vx_px = vx_cms * escala
        vy_px = vy_cms * escala

        # Generar puntos de la trayectoria (función de matematicas.py)
        puntos_cm = predecir_trayectoria(x0=0, y0=0, vx=vx_px, vy=vy_px)
        puntos = [(x0 + px, y0 + py) for (px, py) in puntos_cm]

        key_pred = f"pred_{obj_id}"

        if obj_id not in self._puntos_canvas:
            self._puntos_canvas[obj_id] = {}

        if key_pred not in self._puntos_canvas[obj_id]:
            # Crear la línea punteada de predicción
            coords_flat = [c for p in puntos for c in p]
            linea_pred = self.canvas.create_line(
                *coords_flat,
                fill=COLOR_PREDICT,
                width=1,
                dash=(4, 4)    # patrón punteado: 4px línea, 4px hueco
            )
            self._puntos_canvas[obj_id][key_pred] = linea_pred
        else:
            # Actualizar coordenadas de la línea existente
            coords_flat = [c for p in puntos for c in p]
            self.canvas.coords(
                self._puntos_canvas[obj_id][key_pred],
                *coords_flat
            )


    # Conexión serial y actualización de objetos

    INTERVALO_LECTURA_MS  = 30    # cada cuánto se consume la cola serial
    INTERVALO_LIMPIEZA_MS = 500   # cada cuánto se eliminan objetos perdidos

    def conectar_datos_reales(self, puerto: str, baudios: int = 9600):
        """
        Inicializa el tracker matemático y, si se indicó un puerto,
        arranca la conexión serial real.

        Debe llamarse después de crear la ventana, ej.:
            radar = RadarGUI(master=root)
            radar.conectar_datos_reales("COM5")
        """
        self._tracker = TrackerObjetos()
        self._lector_serial = None

        if puerto is not None:
            self._lector_serial = LectorSerial(puerto, baudios)
            conectado = self._lector_serial.iniciar()

            if conectado:
                print("[RadarGUI] Conexión serial establecida, iniciando lectura.")
                self._consumir_cola_serial()
            else:
                print("[RadarGUI] No se pudo conectar; la ventana queda en modo visual.")
                self._lector_serial = None

        # El loop de limpieza del tracker corre siempre, haya o no
        # conexión real, para mantener consistencia con inicializar_objetos.
        self._limpiar_objetos_tracker()

        # Cerrar el puerto serial correctamente al cerrar la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_cerrar_ventana)

    def _consumir_cola_serial(self):
        """
        Procesa todas las lecturas (angulo, distancia, timestamp)
        acumuladas en la cola del LectorSerial desde la última vez.
        Por cada lectura:
          1. Actualiza el ángulo de la línea de barrido.
          2. Pasa la lectura al tracker, que la asocia a un objeto
             y calcula su velocidad.
          3. Renderiza el objeto actualizado en el canvas.
          4. Dibuja su trayectoria parabólica futura.
        Se reprograma con after() para no bloquear tkinter.
        """
        lecturas = self._lector_serial.obtener_lecturas_pendientes()

        for angulo, distancia, timestamp in lecturas:
            # Sincronizar la línea de barrido con el ángulo real del servo
            self.actualizar_angulo(angulo)

            # -1 indica "sin objeto detectado"; no se crea ni
            # actualiza ningún objeto en ese caso.
            if distancia < 0:
                continue

            obj_id = self._tracker.procesar_lectura(angulo, distancia, timestamp)

            if obj_id == -1:
                continue

            datos_objeto = self._tracker.obtener_objetos_activos()[obj_id]

            self.renderizar_objeto(
                obj_id=obj_id,
                angulo=datos_objeto["angulo"],
                distancia=datos_objeto["distancia"],
                velocidad=datos_objeto["velocidad"]
            )

            self.dibujar_trayectoria(
                obj_id=obj_id,
                vx_cms=datos_objeto["vx"],
                vy_cms=datos_objeto["vy"]
            )

        self.after(self.INTERVALO_LECTURA_MS, self._consumir_cola_serial)

    def _limpiar_objetos_tracker(self):
        """
        Elimina del tracker matemático los objetos que llevan
        demasiado tiempo sin actualizarse, y oculta su
        representación visual correspondiente en el canvas.
        """
        ids_eliminados = self._tracker.limpiar_objetos_perdidos()

        for obj_id in ids_eliminados:
            if obj_id in self._objetos:
                del self._objetos[obj_id]
            if obj_id in self._puntos_canvas:
                for canvas_id in self._puntos_canvas[obj_id].values():
                    self.canvas.coords(canvas_id, 0, 0, 0, 0)
                del self._puntos_canvas[obj_id]
            slot_idx = (obj_id - 1) % len(self._slots_ids)
            self.limpiar_slot(slot_idx)

        self.after(self.INTERVALO_LIMPIEZA_MS, self._limpiar_objetos_tracker)

    def _on_cerrar_ventana(self):
        """
        Handler del cierre de ventana (botón X). Garantiza que
        el hilo serial se detenga y el puerto se cierre limpiamente
        antes de destruir la ventana.
        """
        if self._lector_serial is not None:
            self._lector_serial.detener()
        self.destroy()
    

# Menu principal y navegación

class MenuPrincipal(tk.Tk):
    """
    Ventana raíz del sistema Radar 2D.
    """

    def __init__(self):
        super().__init__()
        self.configurar_ventana()   
        self.cargar_fuentes()   
        self.crear_canvas()        
        self.dibujar_fondo()
        self.dibujar_scanlines()
        self.dibujar_marco_hud()    
        self.dibujar_header()       
        self.dibujar_titulo()   
        self.dibujar_status_bar()
        self.dibujar_botones()
        self.dibujar_footer()  
        self.iniciar_animaciones()


    def configurar_ventana(self):
        """Tamaño, título, color de fondo y centrado en pantalla."""
        self.title("RADAR 2D")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

        # Centrar en cualquier resolución de monitor
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WINDOW_W) // 2
        y = (self.winfo_screenheight() - WINDOW_H) // 2
        self.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def cargar_fuentes(self):
        """
        Define todas las fuentes en un solo lugar.
        """
        self.f_titulo    = tkfont.Font(family=FONT_FAMILY, size=32, weight="bold")
        self.f_subtitulo = tkfont.Font(family=FONT_FAMILY, size=9)
        self.f_boton     = tkfont.Font(family=FONT_FAMILY, size=12)
        self.f_tag       = tkfont.Font(family=FONT_FAMILY, size=8)
        self.f_status    = tkfont.Font(family=FONT_FAMILY, size=9)
        self.f_feedback  = tkfont.Font(family=FONT_FAMILY, size=10)

    def crear_canvas(self):
        """Canvas principal que ocupa toda la ventana."""
        self.canvas = tk.Canvas(
            self,
            width=WINDOW_W,
            height=WINDOW_H,
            bg=COLOR_BG,
            highlightthickness=0   
        )
        self.canvas.pack(fill="both", expand=True)

    def dibujar_fondo(self):
        """
        Carga radar_bg.png, la escala a la ventana y reduce su brillo
        para que sirva de textura sin tapar los elementos de la UI.
        """
        try:
            img = Image.open(BG_IMAGE_PATH).convert("RGB")
            img = img.resize((WINDOW_W, WINDOW_H), Image.LANCZOS)
            img = ImageEnhance.Brightness(img).enhance(0.18)  
            self._bg_photo = ImageTk.PhotoImage(img)          # guardar referencia
            self.canvas.create_image(0, 0, anchor="nw", image=self._bg_photo)
        except FileNotFoundError:
            pass  

    def dibujar_scanlines(self):
        """
        Una línea oscura cada 4 píxeles simula el efecto de una
        pantalla de fósforo verde antigua
        """
        for y in range(0, WINDOW_H, 4):
            self.canvas.create_line(
                0, y, WINDOW_W, y,
                fill=COLOR_SCANLINE,
                width=1
            )

    MARCO_MX = 180   # margen horizontal
    MARCO_MY = 60    # margen vertical

    def dibujar_marco_hud(self):
        """
        Dibuja el marco rectangular del HUD con esquinas decorativas.
        """
        mx, my = self.MARCO_MX, self.MARCO_MY
        mw = WINDOW_W - mx * 2
        mh = WINDOW_H - my * 2

        # Rectángulo de fondo del HUD
        self.canvas.create_rectangle(
            mx, my, mx + mw, my + mh,
            fill=COLOR_HUD_FILL,
            outline=COLOR_GREEN,
            width=1
        )

        # Esquinas decorativas: 4 vértices, cada uno con 2 líneas en L
        corner_size = 12
        vertices = [
            (mx,      my,      +1, +1),   # superior-izquierda
            (mx + mw, my,      -1, +1),   # superior-derecha
            (mx,      my + mh, +1, -1),   # inferior-izquierda
            (mx + mw, my + mh, -1, -1),   # inferior-derecha
        ]
        for (vx, vy, dx, dy) in vertices:
            # Línea horizontal de la L
            self.canvas.create_line(
                vx, vy, vx + dx * corner_size, vy,
                fill=COLOR_GREEN, width=2
            )
            # Línea vertical de la L
            self.canvas.create_line(
                vx, vy, vx, vy + dy * corner_size,
                fill=COLOR_GREEN, width=2
            )

    def dibujar_header(self):
        """
        Dibuja el header del HUD con línea divisoria, etiquetas y punto de estado. 
        """
        mx, my = self.MARCO_MX, self.MARCO_MY

        # Línea divisoria bajo el header
        self.canvas.create_line(
            mx, my + 38, WINDOW_W - mx, my + 38,
            fill=COLOR_GREEN, width=1
        )

        # Etiqueta izquierda
        self.canvas.create_text(
            mx + 14, my + 19,
            anchor="w",
            text="TEC // PROYECTO 2",
            fill=COLOR_GREEN_DIM,
            font=self.f_tag
        )

        # Etiqueta derecha
        self.canvas.create_text(
            WINDOW_W - mx - 28, my + 19,
            anchor="e",
            text="SYSTEMA ONLINE",
            fill=COLOR_GREEN_DIM,
            font=self.f_tag
        )

        # Punto de estado (se parpadea desde iniciar_animaciones)
        self._status_dot = self.canvas.create_oval(
            WINDOW_W - mx - 22, my + 12,
            WINDOW_W - mx - 10, my + 24,
            fill=COLOR_GREEN,
            outline=""
        )

    def dibujar_titulo(self):
        """
        Dibuja el título principal y subtítulo centrados en la parte superior del HUD.
        """
        cx = WINDOW_W // 2

        self.canvas.create_text(
            cx, 162,
            anchor="center",
            text="RADAR 2D",
            fill=COLOR_GREEN,
            font=self.f_titulo
        )

        self.canvas.create_text(
            cx, 196,
            anchor="center",
            text="SISTEMA DE DETECCIÓN",
            fill=COLOR_GREEN_DIM,
            font=self.f_subtitulo
        )

        # Separador decorativo bajo el título
        self.canvas.create_line(
            280, 212, WINDOW_W - 280, 212,
            fill="#003318", width=1
        )

    _ids_status: dict = {}

    def dibujar_status_bar(self):
        """
        Tres campos de estado horizontales.
        
        """
        cx = WINDOW_W // 2
        campos = [
            ("SENSOR", "ESPERANDO", -165),
            ("SERIAL", "LISTO",     0),
            ("GUI",    "ACTIVA",  165),
        ]
        for etiqueta, valor, offset_x in campos:
            item_id = self.canvas.create_text(
                cx + offset_x, 234,
                anchor="center",
                text=f"{etiqueta}: {valor}",
                fill=COLOR_GREEN_MID,
                font=self.f_status
            )
            self._ids_status[etiqueta] = item_id

    def actualizar_status(self, campo: str, valor: str, color: str = COLOR_GREEN_MID):
        """
        API para que otros módulos 
        actualicen los indicadores de estado en tiempo real.

        """
        if campo in self._ids_status:
            self.canvas.itemconfig(
                self._ids_status[campo],
                text=f"{campo}: {valor}",
                fill=color
            )

    BTN_W      = 380
    BTN_H      = 42
    BTN_Y0     = 300   # y del primer botón
    BTN_GAP    = 56    # separación entre botones

    def dibujar_botones(self):
        """
        Crea los 2 botones del menú.
        """
        bx = (WINDOW_W - self.BTN_W) // 2  # x centrado

        opciones_principales = [
            ("01", "►  INICIAR ESCANEO", self._accion_iniciar),
        ]

        for i, (idx, texto, callback) in enumerate(opciones_principales):
            by = self.BTN_Y0 + i * self.BTN_GAP
            self._crear_boton_hud(
                x=bx, y=by,
                texto=f"  {idx}   {texto}",
                callback=callback,
                color_borde=COLOR_GREEN,
                color_fg=COLOR_GREEN
            )

        # Separador visual antes del botón de salir
        sep_y = self.BTN_Y0 + 1 * self.BTN_GAP - 8
        self.canvas.create_line(
            bx, sep_y, bx + self.BTN_W, sep_y,
            fill="#002210", width=1
        )

        # Botón salir
        by_salir = self.BTN_Y0 + 1 * self.BTN_GAP + 4
        self._crear_boton_hud(
            x=bx, y=by_salir,
            texto="  02   ►  SALIR",
            callback=self._accion_salir,
            color_borde=COLOR_GREEN_DARK,
            color_fg=COLOR_GREEN_DIM
        )

        # Label de feedback bajo los botones
        self._lbl_feedback = tk.Label(
            self.canvas,
            text="",
            font=self.f_feedback,
            fg=COLOR_GREEN,
            bg=COLOR_BG
        )
        feedback_y = self.BTN_Y0 + 2 * self.BTN_GAP + 14
        self.canvas.create_window(WINDOW_W // 2, feedback_y,
                                   window=self._lbl_feedback)

    def _crear_boton_hud(self, x: int, y: int, texto: str,
                          callback, color_borde: str, color_fg: str):
        """
        Factoría reutilizable para botones HUD.
        """
        frame = tk.Frame(
            self.canvas,
            bg=color_borde,    # el Frame actúa como borde de 1px
            bd=0,
            padx=1, pady=1
        )
        boton = tk.Button(
            frame,
            text=texto,
            command=callback,
            font=self.f_boton,
            fg=color_fg,
            bg=COLOR_HUD_FILL,
            activeforeground=COLOR_BG,
            activebackground=color_borde,
            relief="flat",
            bd=0,
            anchor="w",
            padx=10,
            cursor="hand2"
        )
        boton.pack(fill="both", expand=True)
        self.canvas.create_window(
            x, y,
            anchor="nw",
            window=frame,
            width=self.BTN_W,
            height=self.BTN_H
        )

    def dibujar_footer(self):
        """
        Línea divisoria y tres campos de texto en la parte inferior
        del marco HUD.
        """
        y_linea = WINDOW_H - self.MARCO_MY + 18   # justo sobre el borde inferior

        self.canvas.create_line(
            self.MARCO_MX, y_linea,
            WINDOW_W - self.MARCO_MX, y_linea,
            fill="#002210", width=1
        )

        campos_footer = [
            (self.MARCO_MX + 14,       "w",      "I SEM 2026"),
            (WINDOW_W // 2,            "center", "PROF. LEONARDO ARAYA"),
            (WINDOW_W - self.MARCO_MX - 14, "e", "TEC // CR"),
        ]
        for (fx, anchor, texto) in campos_footer:
            self.canvas.create_text(
                fx, y_linea + 14,
                anchor=anchor,
                text=texto,
                fill=COLOR_GREEN_DARK,
                font=self.f_tag
            )

    def iniciar_animaciones(self):
        """Arranca todos los loops de animación."""
        self._dot_visible = True
        self._animar_dot()

    def _animar_dot(self):
        """
        Alterna la visibilidad del punto de estado cada 600 ms.
        """
        color = COLOR_GREEN if self._dot_visible else COLOR_HUD_FILL
        self.canvas.itemconfig(self._status_dot, fill=color)
        self._dot_visible = not self._dot_visible
        self.after(600, self._animar_dot)

    def _mostrar_feedback(self, mensaje: str, color: str = COLOR_GREEN):
        """
        Muestra un mensaje bajo los botones por 2.5 segundos.
        """
        self._lbl_feedback.config(text=mensaje, fg=color)
        self.after(2500, lambda: self._lbl_feedback.config(text=""))

    def _accion_iniciar(self):
        """
        Detecta automáticamente el puerto del Arduino, abre la
        ventana del radar y oculta el menú principal mientras
        el radar está activo. Si no se detecta ningún Arduino,
        el radar igual se abre pero en modo visual (sin datos
        reales), y se le avisa al usuario por la barra de estado.
        """
        self.actualizar_status("SENSOR", "BUSCANDO...", COLOR_GREEN_MID)
        self._mostrar_feedback("[ BUSCANDO ARDUINO... ]")

        info_puerto = detectar_puerto_arduino_detallado()

        if info_puerto["encontrado"]:
            puerto = info_puerto["puerto"]
            self.actualizar_status("SENSOR", "CONECTADO", COLOR_GREEN)
            self.actualizar_status("SERIAL", puerto, COLOR_GREEN)
            self._mostrar_feedback(f"[ ARDUINO DETECTADO EN {puerto} ]")
        else:
            puerto = None
            self.actualizar_status("SENSOR", "NO DETECTADO", COLOR_RED_ALERT)
            self._mostrar_feedback(
                "[ ARDUINO NO DETECTADO — MODO VISUAL ]", COLOR_RED_ALERT
            )

        # Pequeña pausa para que el usuario alcance a leer el feedback
        self.after(1200, lambda: self._abrir_radar(puerto))

    def _abrir_radar(self, puerto):
        """
        Oculta el menú principal y abre la ventana del radar.
        """
        self.withdraw()   # oculta el menú sin destruirlo

        ventana_radar = RadarGUI(master=self, puerto=puerto)

        ventana_radar.bind("<Destroy>", self._on_radar_cerrado)

    def _on_radar_cerrado(self, event):
        """
        Vuelve a mostrar el menú principal cuando se cierra la
        ventana del radar.
        """
        if event.widget == event.widget.winfo_toplevel():
            self.deiconify()
            self.actualizar_status("SENSOR", "ESPERANDO", COLOR_GREEN_MID)
            self.actualizar_status("SERIAL", "LISTO", COLOR_GREEN_MID)

    def _accion_salir(self):
        self._mostrar_feedback("[ CERRANDO SISTEMA... ]", COLOR_RED_ALERT)
        self.after(800, self.destroy)

    def _mostrar_feedback(self, mensaje: str, color: str = COLOR_GREEN):
        self._lbl_feedback.config(text=mensaje, fg=color)
        self.after(2500, lambda: self._lbl_feedback.config(text=""))

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()