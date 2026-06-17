"""
Script de verificacion - Radar 2D
==================================
Lee los datos que manda el Arduino por puerto serial
(formato: angulo,distancia) y los muestra en consola.

Este script NO es la GUI final del proyecto, es solo para
confirmar que los datos llegan bien formateados antes de
pasarle el trabajo a quien haga la interfaz grafica.

Requisitos:
    pip install pyserial

Antes de correr:
    1. Verificar que el Arduino ya tenga el sketch radar_final.ino subido
    2. Cambiar PUERTO al puerto COM que te aparecio en el Administrador
       de Dispositivos (en este caso, segun lo que reportaste: "COM5")
    3. Cerrar el Monitor Serial del Arduino IDE antes de correr este
       script (el puerto serial solo lo puede usar un programa a la vez)
"""

import serial
import time

# ---------------- Configuracion ----------------
PUERTO = "COM5"      # Cambiar segun el puerto que te aparezca a ti
BAUDIOS = 9600        # Debe coincidir con el Serial.begin() del Arduino


def conectar_arduino(puerto, baudios):
    """Intenta abrir la conexion serial con el Arduino."""
    try:
        conexion = serial.Serial(puerto, baudios, timeout=1)
        print(f"Conectado a {puerto} a {baudios} baudios.")
        # Pequena espera para que el Arduino termine de reiniciar
        # (al abrir el puerto serial, el Arduino se reinicia automaticamente)
        time.sleep(2)
        return conexion
    except serial.SerialException as error:
        print(f"No se pudo conectar a {puerto}.")
        print(f"Detalle del error: {error}")
        print("Revisa que el puerto sea el correcto y que el Monitor")
        print("Serial del Arduino IDE este cerrado.")
        return None


def parsear_linea(linea):
    """
    Convierte una linea de texto 'angulo,distancia' en una tupla
    de numeros (angulo, distancia). Retorna None si la linea no
    tiene el formato esperado.
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


def main():
    conexion = conectar_arduino(PUERTO, BAUDIOS)

    if conexion is None:
        return

    print("Leyendo datos del radar. Presiona Ctrl+C para detener.\n")
    print(f"{'Angulo (grados)':<18}{'Distancia (cm)':<18}{'Estado'}")
    print("-" * 50)

    try:
        while True:
            linea_cruda = conexion.readline().decode("utf-8", errors="ignore")

            if not linea_cruda:
                continue  # no llego nada en este ciclo, seguimos esperando

            datos = parsear_linea(linea_cruda)

            if datos is None:
                print(f"[Linea con formato inesperado]: {linea_cruda.strip()}")
                continue

            angulo, distancia = datos

            if distancia == -1:
                estado = "Fuera de rango"
                texto_distancia = "---"
            else:
                estado = "OK"
                texto_distancia = str(distancia)

            print(f"{angulo:<18}{texto_distancia:<18}{estado}")

    except KeyboardInterrupt:
        print("\nLectura detenida por el usuario.")

    finally:
        conexion.close()
        print("Puerto serial cerrado correctamente.")


if __name__ == "__main__":
    main()
