// ============================================================
// RADAR 2D - Proyecto 2
// Fundamentos de Sistemas Computacionales
// ============================================================
// Este sketch controla el servo y el sensor ultrasonico,
// y envia por puerto serial los datos en formato:
//   angulo,distancia
// Ejemplo: "94,37"  -> servo en 94 grados, objeto a 37 cm
// Si no detecta nada, distancia se envia como -1
// ============================================================

#include <Servo.h>

// ---------------- Configuracion de pines ----------------
const int PIN_TRIG = 9;
const int PIN_ECHO = 10;
const int PIN_SERVO = 6;
const int PIN_LED_ALERTA = 13;

// ---------------- Configuracion del barrido ----------------
const int ANGULO_MIN = 0;
const int ANGULO_MAX = 180;
const int PASO_GRADOS = 2;     // cada cuantos grados toma una lectura
const int DELAY_SERVO_MS = 40; // tiempo de espera tras mover el servo

// ---------------- Configuracion de alerta ----------------
const long DISTANCIA_ALERTA_CM = 15; // si detecta algo mas cerca que esto, prende LED

Servo miServo;
int anguloActual = ANGULO_MIN;
int direccion = 1; // 1 = subiendo, -1 = bajando

void setup() {
  Serial.begin(9600);

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED_ALERTA, OUTPUT);

  miServo.attach(PIN_SERVO);
  miServo.write(anguloActual);
  delay(500); // tiempo para que el servo llegue a la posicion inicial
}

long leerDistanciaCM() {
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  long duracion = pulseIn(PIN_ECHO, HIGH, 30000); // timeout 30ms (~5m max)

  if (duracion == 0) {
    return -1; // fuera de rango, no hubo eco
  }

  long distancia = duracion * 0.034 / 2; // cm
  return distancia;
}

void actualizarLedAlerta(long distancia) {
  if (distancia != -1 && distancia <= DISTANCIA_ALERTA_CM) {
    digitalWrite(PIN_LED_ALERTA, HIGH);
  } else {
    digitalWrite(PIN_LED_ALERTA, LOW);
  }
}

void enviarLectura(int angulo, long distancia) {
  Serial.print(angulo);
  Serial.print(",");
  Serial.println(distancia);
}

void loop() {
  // Mover el servo a la posicion actual
  miServo.write(anguloActual);
  delay(DELAY_SERVO_MS);

  // Tomar lectura del sensor
  long distancia = leerDistanciaCM();

  // Actualizar LED de alerta segun la distancia detectada
  actualizarLedAlerta(distancia);

  // Enviar el dato por serial: angulo,distancia
  enviarLectura(anguloActual, distancia);

  // Calcular el siguiente angulo (barrido continuo ida y vuelta)
  anguloActual += PASO_GRADOS * direccion;

  if (anguloActual >= ANGULO_MAX) {
    anguloActual = ANGULO_MAX;
    direccion = -1; // empieza a bajar
  } else if (anguloActual <= ANGULO_MIN) {
    anguloActual = ANGULO_MIN;
    direccion = 1; // empieza a subir
  }
}
