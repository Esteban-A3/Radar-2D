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
            highlightthickness=0   # sin borde gris de tkinter
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


if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()