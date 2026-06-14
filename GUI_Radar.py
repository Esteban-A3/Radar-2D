import tkinter as tk
from tkinter import font as tkfont
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

if __name__ == "__main__":
    app = MenuPrincipal()
    app.mainloop()