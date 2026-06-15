import tkinter as tk
from tkinter import font as tkfont
from PIL import Image, ImageTk, ImageEnhance
import os


COLOR_BG         = "#000000"   # negro puro 
COLOR_GREEN      = "#00FF46"   # verde radar 
COLOR_GREEN_MID  = "#00CC38"   # verde medio 
COLOR_GREEN_DIM  = "#00994A"   # verde apagado 
COLOR_GREEN_DARK = "#006628"   # verde oscuro
COLOR_HUD_FILL   = "#000D04"   # negro verdoso
COLOR_RED_ALERT  = "#FF2222"   # rojo 
COLOR_SCANLINE   = "#001A08"   # verde muy oscuro

FONT_FAMILY = "Courier"        
WINDOW_W = 900
WINDOW_H = 620

# Ruta relativa a la imagen de fondo
BG_IMAGE_PATH = os.path.join(os.path.dirname(__file__), "assets", "radar.png")


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
            text="SYSTEM ONLINE",
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


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()