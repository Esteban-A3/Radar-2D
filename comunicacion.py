import serial
import time
import threading
import queue

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
