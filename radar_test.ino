#include <Servo.h>

// Pines
const int PIN_TRIG = 9;
const int PIN_ECHO = 10;
const int PIN_SERVO = 6;
const int PIN_LED = 13;

Servo miServo;

void setup() {
  Serial.begin(9600);

  pinMode(PIN_TRIG, OUTPUT);
  pinMode(PIN_ECHO, INPUT);
  pinMode(PIN_LED, OUTPUT);

  miServo.attach(PIN_SERVO);

  Serial.println("Iniciando prueba de componentes...");
}

long leerDistanciaCM() {
  // Disparamos el pulso ultrasonico
  digitalWrite(PIN_TRIG, LOW);
  delayMicroseconds(2);
  digitalWrite(PIN_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(PIN_TRIG, LOW);

  // Medimos cuanto tarda en regresar el eco
  long duracion = pulseIn(PIN_ECHO, HIGH, 30000); // timeout 30ms

  if (duracion == 0) {
    return -1; // no detecto nada (fuera de rango)
  }

  // velocidad del sonido ~0.034 cm/us, dividido 2 porque es ida y vuelta
  long distancia = duracion * 0.034 / 2;
  return distancia;
}

void test_servo_barrido() {
  for (int angulo = 0; angulo <= 180; angulo += 10) {
    miServo.write(angulo);
    delay(200);

    long dist = leerDistanciaCM();
    Serial.print("Angulo: ");
    Serial.print(angulo);
    Serial.print(" | Distancia: ");
    if (dist == -1) {
      Serial.println("fuera de rango");
    } else {
      Serial.print(dist);
      Serial.println(" cm");
    }
  }
}

void loop() {
  digitalWrite(PIN_LED, HIGH);

  test_servo_barrido();

  digitalWrite(PIN_LED, LOW);
  delay(500);
}
