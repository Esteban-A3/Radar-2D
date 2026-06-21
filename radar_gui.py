import tkinter as tk
from tkinter import font as tkfont

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
        