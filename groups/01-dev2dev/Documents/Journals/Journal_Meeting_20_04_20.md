# I&S Gruppe 1 - Freedom Drop - Meeting 20.04.2020
## Diskussion

Teilnehmer:

Christian F Tschudin ([@tschudin](https://github.com/tschudin))
Mateusz Palasz ([@MateuszPalasz](https://github.com/MateuszPalasz))
Oliver Weinmeier ([@oliverweinm](https://github.com/oliverweinm))
Tim Keller ([@TK5-Tim](https://github.com/TK5-Tim))

### Ablauf
*	Gesamtbild besprochen (Big Picture)
	*	Ganze Dateien sollen verschickt werden
	*	Log merge richtig interpretiert
		*	Log sync nicht relevant für unser Projekt
			*	log sync gleicht die Interferenz auf einzelne Dateinen aus
	* Connection setup erstellen, um zu wissen, was die andere Seite Macht
*	Fortschritt Datenaustausch
	*	nur Pseudocode
	*	Hauptaugenmerkmal connection zwischen Wifi und Bluetooth
		*	wie stark ist die Überlappung
	*	**/TODO**: flow chart für Verbindungs Protokoll erstellen
		*	Annährung an bereits vorhandene Protokolle
	* Frage unserer Seits: Wieso können wir nicht alles per Bluetooth verschicken
		*	Wegen dem Geschwindigkeitsvorteil
*	Workflow_Log_Exchange besprochen
	*	Flow chart macht Log merge teilweise
	*	Ast no diffrence
		* Leere Datei als Zeichen für no diff
*	Bezug auf unseren Pseudocode
	*	Service definieren
	*	Devices finden
	*	Parameter und Format(ID) für Wifi finden
	*	Per Ad-Hoc Netz direkt untereinander kommunizieren
		*	Wie würde dabei der Datenaustausch aussehen?
			*	Kein UDP etc. möglich
			*	Eigenes Protokoll schreiben
	*	Nirgends soll IP verwendet werden, nur service name/ service discovery
	*	**/Wunsch** Austauschformat Pcap, wie bei sneakernet
		*	Ansatz: Pcap als Datenbank
		*	inklusive Log merge von uns
*	Weiteres Vorgehen
	*	Konkrett in die Schnittstellen
		*	schmall und tief
	* Fokus auf Übertragungstechnologie beibehalten
	* Zwei Hauptteile, auf die wir unsere Aufmerksamkeit setzen
		* Verbingung herstellen + Daten austausch (Oliver + Mateusz)
		* Austauschformat Pcap (Tim)



### Agenda

##### 24.4 (NEU)
* nächstes Meeting
* Zwischenstand

##### Bis Ende April
* Funktionalität eigenes Teilprojekt fertigstellen

##### Mai
* Teilprojekt zu Gesamtprojekt zusammenfügen
