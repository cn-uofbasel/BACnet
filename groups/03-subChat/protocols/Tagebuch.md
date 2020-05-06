# I&S Security Gruppe 03_SubChat 
##### Dokumentation
#
> Dieses Dokument dient der Nachvollziehbarkit unseres Prozesses. Es soll uns vor allem dazu helfen, das finale Protokoll zu erstellen (Referenzieren und Vollständigkeit). 
> Dieses Dokument soll immer nach dem erreichen von Meilensteinen oder Besprechungsterminen vervollständigt werden. Die dazugehörigen Protokolle sind [hier](https://github.com/cn-uofbasel/BACnet/tree/master/groups/03-subChat/Protokols) zu finden.

### Content Table
1. [Meilenstein: Prototyp fertig](#Meilenstein:_Prototyp)

### Meilenstein:_Prototyp
Der Prototyp inclusive der abgeänderten Datenbank ist zu finden in /BACnet/groups/03-subChat/Prototyp
Beim Prototyp handelt es sich um ein Interface, geschrieben in TkInter. Man startet es mit:
```
python3 UI.py
```
Es wurde folgendes Implementiert:
* Man kann sich als User Anmelden. Im Moment aber nur als Bob oder Alice. Funktionen welche überprüfen, ob ein UserProfil bereits vorhanden ist, sind bereits geschrieben aber noch nicht vollständig implementiert worden.
* Sobald man sich im Chat Feld befindet, werden alle eingaben per enter oder klick auf "send" direkt abgespeichert im .pcap file des users und sogleich wieder rausgeholt und dem Textfeld hinzugefügt mit Info: wer wann was geschrieben hat.
* Drückt man auf Update, so holt der Prototyp die noch ausstehenenden Nachrichten aus dem .pcap file des Kommunikationspartners und fügt sie dem Chat verlauf hinzu. Topologisch sortiert wird dabei noch nicht. Sendet man also nachtichten ohne auf update zu klicken, so werden diese im Nachhinein nich korrekt zeitlich eingeordnet. Ein einfacher fixx dafür wäre ein thread welcher ständig prüft, b bereits neue Daten im .pcap file des Partners niedergeschrieben wurden.
