# Proyecto Radar con Arduino 📡

Este repositorio contiene el código fuente y el esquema de conexiones para un sistema de radar utilizando un Arduino, un sensor ultrasónico y un servomotor.


## 📂 Contenido del Repositorio

El proyecto está compuesto por los siguientes archivos:

* **`Conexiones de Componentes a Arduino`**: Archivo con el detalle técnico, pines y notas sobre cómo conectar cada componente físico a la placa Arduino.
* **`radar_final.ino`**: Archivo principal y definitivo con la programación completa del proyecto del radar.
* **`radar_test.ino`**: Script de prueba inicial para validar el correcto funcionamiento de los componentes por separado.
* **`radar_test2.ino`**: Segunda prueba de control y calibración antes de la integración final.

---

## 🛠️ Componentes Utilizados

A grandes rasgos, el circuito integra los siguientes elementos:
1.  **Sensor Ultrasónico (HC-SR04):** Para medir las distancias.
2.  **Servomotor:** Para rotar el sensor y lograr el barrido de 180 grados.
3.  **LED Rojo:** Indicador de alerta de proximidad.
4.  **Placa Arduino** (y resistencias correspondientes).

---

## 🚀 Cómo Empezar

1.  Revisa el archivo de **Conexiones de Componentes** para armar el circuito correctamente en tu protoboard.
2.  Si deseas probar los componentes de forma individual, carga primero `radar_test.ino` o `radar_test2.ino`.
3.  Para poner en marcha el radar completo, abre y sube el archivo `radar_final.ino` a tu Arduino desde el IDE oficial.
