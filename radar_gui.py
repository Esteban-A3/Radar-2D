import tkinter as tk
from tkinter import font as tkfont
import math

# Colores del menu y HUD
COLOR_BG         = "#000000"
COLOR_GREEN      = "#00FF46"
COLOR_GREEN_MID  = "#00CC38"
COLOR_GREEN_DIM  = "#00994A"
COLOR_GREEN_DARK = "#006628"
COLOR_HUD_FILL   = "#000D04"
COLOR_RED_ALERT  = "#FF2222"
COLOR_SCANLINE   = "#001A08"

# Colores de la pantalla radar
COLOR_SWEEP      = "#00FF46"   # línea de barrido (verde brillante)
COLOR_SWEEP_FADE = "#003318"   # estela del barrido
COLOR_OBJECT     = "#00FF46"   # punto de objeto detectado
COLOR_PREDICT    = "#FF6600"   # línea de predicción parabólica
COLOR_RING       = "#003D1A"   # anillos de distancia (sutil)
COLOR_GRID       = "#002210"   # líneas de la rejilla angular

FONT_FAMILY = "Courier"

WINDOW_W = 1000
WINDOW_H = 700

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

    def __init__(self, master=None):
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

    def configurar_ventana(self):
        self.title("RADAR 2D — ESCANEO ACTIVO")
        self.geometry(f"{WINDOW_W}x{WINDOW_H}")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.update_idletasks()
        x = (self.winfo_screenwidth()  - WINDOW_W) // 2
        y = (self.winfo_screenheight() - WINDOW_H) // 2
        self.geometry(f"{WINDOW_W}x{WINDOW_H}+{x}+{y}")

    def cargar_fuentes(self):
        self.f_tag      = tkfont.Font(family=FONT_FAMILY, size=8)
        self.f_label    = tkfont.Font(family=FONT_FAMILY, size=9)
        self.f_titulo   = tkfont.Font(family=FONT_FAMILY, size=11, weight="bold")
        self.f_dato     = tkfont.Font(family=FONT_FAMILY, size=10)
        self.f_velocidad= tkfont.Font(family=FONT_FAMILY, size=8)

    def crear_canvas(self):
        self.canvas = tk.Canvas(
            self,
            width=WINDOW_W,
            height=WINDOW_H,
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
        for y in range(0, WINDOW_H, 4):
            self.canvas.create_line(
                0, y, WINDOW_W, y,
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
            self.PANEL_X, 0, self.PANEL_X, WINDOW_H,
            fill=COLOR_GREEN, width=1
        )

        # Header superior
        self.canvas.create_line(
            0, 40, WINDOW_W, 40,
            fill=COLOR_GREEN, width=1
        )
        self.canvas.create_text(
            WINDOW_W // 2, 20,
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
                WINDOW_W - 10, 82,
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
                    WINDOW_W - 10, y0 + 68,
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
    