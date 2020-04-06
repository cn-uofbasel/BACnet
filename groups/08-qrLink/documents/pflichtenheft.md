# Pflichtenheft

### 1. Visionen und Ziele 
/V10/ Wir möchten eine grafischen Input, welches mittels Tablet oder einem Pad erstellt wird, in ein Format kodieren.
/V20/ Durch scannen eines QR Codes über die WebCam, wird der grafische Input dem Partner geschickt und dort wieder entziffert.
/Z10/ Ziel dieses Projektes ist, einen grafischen Input, welches mittels Tablet/Pad erstellt wird, via QR Code von einem zum anderen Laptop zu senden ohne Internet.


### 2. Stakeholder 
/S10/ Auftraggeber, Systemadministratoren, Entwickler: Li Ting Luong, Monika Multani 
/S20/ First level support: Christian Tshudin, Claudio Alexander Marxer und Christopher Scherb
/S30/ Management: Universität Basel 
/S40/ Endbenutzer: BACnet Benutzer
/S50/ BACnet Entwicklier

### 3. Rahmenbedingungen 
/R10/ Einhalten der Lizenzvorgaben 
/R20/ ohne Internet 

### 4. Relevanter Kontext 
/K10/ Introduction to Internet and Security Projekt 2020, Universität Basel 

### 5. Use Case 
##### Use Case 1: 

Name: grafischer Input erstellen 
Akteure: Benutzer
Vorbedingungen: Tablet/Pad und Laptop notwendig 
Standardablauf 
* Tablet/Pad wird mit dem Laptop verbunden.
* Programm wird geöffnet.
* Auf dem Tablet/Pad wird eine Grafik gezeichnet.
* Grafischer Input wird auf dem Bildschirm im Programm ersichtlich.
Nachbedingungen Erfolg: Grafischer Input wird korrekt auf dem Bildschirm angezeigt.
Nachbedingung Fehlschlag: Der Input entspricht nicht dem eingegebenen Input. 

##### Use Case 2: 

Name: grafischer Input über QR Code senden
Akteure: 2 Benutzer, welche den grafischen Input austauschen möchten
Vorbedingungen: Tablet/Pad und LapTop mit einer WebCam notwendig
Standardablauf 
* Grafischer Input wird durch Tablet/Pad auf dem Laptop erstellt.
* Grafischer Input wird auf dem Bildschirm im Programm ersichtlich.
* QR Code wird für diesen Input erstellt, welches der Partner über seine WebCam scannt.
* Grafischer Input wird an den Partner geschickt und erscheint auf seinem Bildschirm.
Nachbedingungen Erfolg: Der grafische Input wird auf dem anderen LapTop ersichtlich.
Nachbedingung Fehlschlag: Der grafische Input entspricht nicht dem Output auf dem anderen LapTop.

### 6. Funktionale Anforderungen 
/F10/ Funktion 1: Grafischer Input muss eingelesen werden.
/F20/ Funktion 2: Grafischer Input muss auf dem Bildschirm ersichtlich werden.
/F30/ Funktion 3: Für einen grafischen Input muss ein QR Code erstellt werden. 
/F40/ Funktion 4: Durch scannen des QR Codes, muss der grafische Input an den Partner gesendet werden. 
/F50/ Funktion 5: Auf dem Bildschirm des Partners muss der grafische Output ersichtlich werden.

### 7. Nichtfunktionale Anforderungen 
/NF10/ Anforderung 1: Der grafische Input sollte während gezeichnet wird innerhalb von 3 Sekunden auf dem Bildschirm ersichlich sein. 
/NF20/ Anforderung 2: Grafischer Input sollte nach dem Scannen des QR Codes auf dem Bildschirm des Partners innerhalb von 3 Sekunden ersichtlich sein. 

#### 8. Qualitätsanforderungen 
/QF10/ Der grafische Input muss richtig kodiert und dekodiert werden.
/QE10/ Alle Reaktionszeiten auf Benutzeraktionen müssen unter 5 Sekunden liegen. 

### 9. Abnahmekriterien 
/A10/ Grafischer Input auf dem Bildschirm anzeigen.
/A20/ Nach dem Scannen des QR Codes wird der grafische Input auf dem LapTop des Partners ersichlich.
/A30/ Funktioniert ohne Absturz und erzeugt keine Laufzeitfehler. 