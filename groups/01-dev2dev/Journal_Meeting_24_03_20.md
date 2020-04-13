# I&S Gruppe 1 - Freedom Drop - Meeting 24.03.2020
## Besprechung der grundsätzlichen Rahmenbedingungen und Herausforderungen des Projekts.

Teilnehmer: 
Christian F Tschudin ([@tschudin](https://github.com/tschudin))
Christopher Scherb ([@blacksheeep](https://github.com/blacksheeep))
Mateusz Palasz ([@MateuszPalasz](https://github.com/MateuszPalasz))
Oliver Weinmeier ([@oliverweinm](https://github.com/oliverweinm))
Tim Keller ([@TK5-Tim](https://github.com/TK5-Tim))


* Grundsätzliche Funktionalität mit Bluetooth & Wifi -> Übertragungstechnologie
* Hauptziel: Synchronisierung der Logs. Geschwindigkeit zweitranig. 
* Anbindung an Datenbank: Was muss importiert/exportiert werden? Heuristiken müssen definiert.
* Zusammenarbeit Gruppe 4, 7, 12 

#### Vereinfachter Dateitransfer
* Konzepte klären 
* Anschließend Hauptsächlich Bluetooth 
* Falls zeitlich möglich Einbindung Wifi
* Ohne config: Keine IP-Adressen, "nacktes" Bluetooth 
* Ganze Dateien statt einzelne Blöcke
* Perfekte Bluetooth Verbindung bringt nix, falls Anbindung nicht gegeben
* log: jeder Eintrag hat Namen, hilft bei der Unterscheidung
* nicht angewiesen auf lauffähige Applikation beim Testing 

### Security
* Handshake ?
* nicht von Anfang an intern verschlüsselt? Schlüsselübergabe Später
* Datenbank erkennen können 
* Peering als Verbinden zur Datenbank -> UI -> Code zur Verbindung?

### Agenda
##### Bis 1.4. 
* grundsätzlich große Fragen klären.
* Gerätekombinationen (gegebenenfalls Sollbruchstelle)
* Was ist möglich und wie umsetzbar?
* abklären Rahmenbedingungen Programmiersprachen
##### Bis 16.4. 
* Konzepte sind durchdacht und schlüssig
* möglicherweise erste Implementierungen vorführen
* Rahmenbedingungen für Zusammenarbeit mit anderen Gruppen klären
##### Bis Ende April 
* Funktionalität eigenes Teilprojekt fertigstellen
##### Mai 
* Teilprojekt zu Gesamtprojekt zusammenfügen