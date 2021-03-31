
# Sensor Protocol
## Sensor Definition
 * **ID**
 * **Label**
 * **Description**
 * **Properties**
   * Sensor type (e.g. *NTC, Photo diode*)
   * Sensor description (e.g. *VISHAY NTCLE100E3152JB0*)
   * Physical quantity (e.g. *Temperature, luminous flux*)
   * Unit (e.g. *K / °C, lm*)
   * Interval (e.g. *300 s*)
 * **Location**
   * Coordinates
     * Longitude
     * Latitude
     * Altitude
   * Description (e.g.. *Measuring station X at forest Y*)
   
## Sensor Readings
 * **ID**
 * **Timestamp** (CET / UTC+1, unix time?)
 * **Reading** (64 bit floating point / double ?)
 
---
### GERMAN VERSION
  # Sensor-Protokoll
 ## Sensor-Definition
 * **ID**
 * **Kurzbezeichnung**
 * **Beschreibung**
 * **Eigenschaften**
   * Sensor-Typ (z.B. *NTC, Foto-Diode*)
   * Sensor-Bezeichnung (z.B. *VISHAY NTCLE100E3152JB0*)
   * Physikalische Grösse (z.B. *Temperatur, Lichtstrom*)
   * Einheit (z.B. *K / °C, lm*)
   * Intervall (z.B. *300 s*)
 * **Ort**
   * Koordinaten
     * Längengrad
     * Breitengrad
     * Höhe
   * Beschreibung (z.B. *Messstation X im Wald Y*)
   
## Sensor-Werte
 * **ID**
 * **Zeitstempel** (CET / UTC+1)
 * **Messwert** (64 bit floating point / double ?)