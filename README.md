# SMSReader
 
SMSReader is a simple Soil Moisture Sensor reader for `micropython` and `Raspberry Pi Pico W`. For testing purposes, it need the Development board, the MAX485 sensor and the soid moisture sensor.

The soil moiture sensor has the following characteristics:
 - Soil temperature:
 - Range: -40~80°C;
 - Resolution: 0.1°C;
 - Accuracy: ±0.5°C
 - Soil Moisture:
 - Range: 0-100%RH;
 - Resolution: 0.1%RH;
 - Accuracy: 5%
 - Supply voltage: DC5V-24V
 - Signal output: RS485, Modbus protocol Measurement principle: soil moisture FDR method Protection grade: IP68 can be used for a long time
 - when immersed in water Operating environment: -40~85°C
 - Probe material: anti-corrosion special electrode Sealing material: black flame retardant epoxy resin
 - Communication parameters: baud rate 9600, 8 data bits, no parity bit
 - The interval between two communications should be at least 1000ms or more

The schematic of the project is the following:

![Schematic](/assets/schematic.png)

Sources files are in the `src` folder. The main file is `main.py`, which is the entry point of the project. `functions.py` contains some useful functions to read the sensor data. And `secrets.json` contains the configuration of the project.