import serial.tools.list_ports

def listar_puertos_disponibles() -> list:
    """
    Retorna todos los puertos seriales detectados por el sistema
    operativo, sin filtrar. Útil para depuración y para mostrar
    al usuario qué se detectó si la búsqueda automática falla.

    Returns:
        Lista de objetos serial.tools.list_ports_common.ListPortInfo
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