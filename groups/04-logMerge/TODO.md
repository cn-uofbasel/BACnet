Von unten nach oben:

Transportschicht ruft unser Programm auf.
Parameter an uns: 
* Pfad für neue .pcap-Logs

1. Extrahieren der einzelnen "events" aus den pcap.-Logs
2. Suchen nach neuen follow/unfollow events und mitteilung an feedCtrl (aktualisierung whitelist)
3. Filterung mithilfe des feedCtrl
4. Speicherung der neuen Events in der Datenbank

Von oben nach unten: 

Transportschicht ruft unser programm auf.

Parameter an uns: 
* Liste mit verbundenen Feed-Ids und dazugehörigem Zeitstempel letzter Aufruf
* anzahl maximale paketanzahl

1. feedCtrl die liste mit feed-ids weitergeben
2. feedCtrl fragen welche logs (feed-ids) weitergeschickt werden
3. mithilfe von feedctrl filtern
4. logs in .pcap konvertieren (zuerst eigener log, dann fremdlogs, nach max paketzahl abbrechen)
5. daten an transportschicht ubergeben

