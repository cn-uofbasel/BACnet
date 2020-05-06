Gruppe 4 macht den merge in die Datenbank und überprüft ob und welche Nachrichten in die DB 
kommen.
Ein USB Netzwerk ist wie ein Sub-Netzwerk oder separaten User zu behandeln.
Wir halten Metadaten fest, welche Nutzer den USB Stick benutzen.
Diese können in einer kleinen Textdatei gedumpt werden, denn wir benötigen dies später.

Hierzu würden wir zwei Funktionen nutzen, die dann auf ihre Funktionen zugreifen.

Mockup für die Funktionen:
Zu finden sollten diese merge Funktionen der Gruppe 4 an einem passenden Ort, damit wir diese finden.
(Alternative ihre Logik als package bei uns mit rein?)

Export(int Anzahl_Nachrichten, string Pfad_der_pcap_Dateien_auf_USBStick, 
        Liste_aller_Nutzer_die_USBStick_verwenden)
        
Import(Pfad_der_pcap_Dateien_auf_USBStick)

Die Liste der User sollte so aussehen:
Users = [(feedID, lastLogin), (feedID2, lastLogin)]