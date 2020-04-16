# Protokoll der Besprechung vom 13.04.2020

## Wie soll der Prototyp aussehen?
* Wir waren uns unklar darüber, wie der gewünschte Prototyp aussehen sollte. Uns war nach der Erstbesprechung nicht ganz klar, dass die von Herrn Tschudin erwähnte Datenbank bereits auf Git vorhanden war. Deshalb haben wir einen Prototyp entwickelt, welcher mit der Aufgabe 3 (vom Übungsblatt 3 der Internet & Security Vorlesung) funktioniert hat. Dieser Prototyp hat zwar funktioniert (man konnte den Server starten, die Daten des Anderen Clients bekommen und sich mit diesem Verbinden. Im Hintergrund wurden Nachrichten dann auch verschickt aber da die Aufgabe mit select() geschrieben wurde, ist uns das TkInter User Interface immer eingefrohren an genau dieser Stelle.
* Herr Tschudin machte uns klar, dass er von der oben Verlinkten Datenbank gesprochen hatte und nahm sich dann sogar die Zeit, uns diese grob zu erklären was uns sehr weitergeholfen hat.
* Wir haben uns dann dazu entschieden, den Prototypen umzuschreiben, sodass er mit der Bereitgestellten Datenbank funktioniert in seinen Elementaren Funktionen (Client anmelden als User, Nachrichten schreiben, Nachrichten rausholen (Antworten vom anderen Client).

## Klarheit über die Demo Datenbank die von Herrn Tschudin bereitgestellt wurde
Wir haben mehr darüber erfahren, wie [die Datenbank](https://github.com/cn-uofbasel/BACnet/tree/master/src/demo/lib) in /BACnet/src/demo/lib funktioniert und zu bedienen ist. Dies ist alles [hier](https://github.com/cn-uofbasel/BACnet/blob/master/src/demo/README.md) weiter noch beschrieben. Dabei sind folgende Befehle für uns wichtig:

> Erstellen eines Keys:
> '''
> ./crypto.py >alice.key
> '''
> Erstellen eines pcap files (mit Option einen Eintrag hinzuzufügen. Wenn nicht gewollt, Abbrechbar mit Ctrl + c um nur .pcap zu erstellen):
> '''
> ./feed.py --keyfile alice.key alice.pcap create
> '''
> Einträge müssen dabei so geschrieben werden: \["write entries like this!"]
> Um Einträge einzusehen schreibt man:
> '''
> ./feed.py alice.pcap dump 
> '''
> und um Einträge hinzuzufügen zu einem .pcap file führt man folgenden befehl aus:
> '''
> ./feed.py --keyfile alice.key alice.pcap append
> '''
> Einträge müssen dabei wiederum so geschrieben werden: \["write entries like this!"]

## Genaueres
Herr Tschudin hat uns folgende Grafik auf ein Whiteboard gezeichnet als Idee, wie der Prototyp funktionieren soll:
![image](Grafiken/.../Grafiken/Datenbank.jpeg)

## Wo kann das Projekt hingehen?
* Realtime vs manual update
* Bilder versenden statt nur nachrichten
* Feeds implementieren
* Einfache Variante: alles angezeigte löschen und neu laden aus dem .pcap file beim updaten. Schwieriger: nur Material laden, welches noch nicht bereits vorhanden ist.
* Topologische Sortierung der Nachrichten damit sie in der richtigen Rheienfolge angezeigt werden (dies wird jedoch bereits für uns gemacht haben wir im Nachhinein bei der Besprechung am 14.04.2020 mit Gruppe 7 erfahren.)
