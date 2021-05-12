# Projektverlauf BACnet-Core
## Raphael Kreft, Tim Bachmann, Nico Aebischer - FS21

### 07.04.21
Projektidee wurde besprochen und schon angenommen.



#### 11.04.21
Kickoff-Meeting: Idee wurde klarer formuliert und erste Arbeitsschritte besprochen.
Sind dabei verblieben, uns bis zum nächsten Meeting in die Reports einzulesen, ohne
uns schon allzu sehr auf den Core zu fokussieren. Der Überblick über das Gesamtprojekt
sollte zunächst gesichert werden.



### 20.04.21
Reports wurden individuell durchgelesen und erste Erkenntnisse besprochen. Der Core
konnte nun klar von den anderen Projekten abgegrenzt werden. Gesamtüberblick war aber
auch noch Thema. Aufgabe bis zum nächsten Meeting war, nun nochmals die Reports der
für den Core relevanten Gruppen genauer durchzugehen und sich dabei auch in den entsprechenden
Code einzulesen.



### 28.04.21
Ein erstes Dokument wurde erstellt, dass der Übersicht dienlich sein soll. Es erklärt, wie
das BACnet aufgebaut ist und geht dabei auf das Secure Scuttlebutt Prinzip sowie auf die
grundlegenden Strukturen des BACnet ein, wie zum Beispiel Feeds / Masterfeeds, Events und die
Datenbank.  
Auf das nächste Meeting soll individuell eine grobe Übersicht über den Core erstellt werden, anhand
der die weitere Planung gemacht werden kann.



### 04.05.21
Die Implementierungsvorschläge für die BACnet-Core Struktrur wurden diskutiert und man hat sich auf
eine grobe Richtung geeinigt. Ziel bis zum nächsten Meeting war, diese Grobstruktur nochmals durchzudenken
und für die einzelnen Bestandteile zu definieren, was sie genau beinhalten sollten, respektive welche
Funktionalitäten sie anbieten sollen.



### 08.05.21
Die Gesamtstruktur und vor allem die Herangehensweise an unser Projekt wurde nochmals überdacht. Man hat sich
darauf geeinigt, eine Art Top-Down Approach zu machen. Vorher wollten wir unser Projekt anhand der Usages des 
Cores von anderen Gruppen aufbauen, also erst eine Art Interface-Definition machen, um dann darum unsere
Struktur zu machen. Wir könnten so aber in Gefahr laufen, auf dem Chaos des vorangehenden Jahres aufzubauen. 
Damals wurde das BACnet Projekt gestartet und jede Gruppe hat zunächst für sich selbst geschaut. Anschliessend
hat man dann die einzelnen Projekte in ein Ganzes zusammengefügt, wobei ein etwas unübersichtlicher Flickenteppich 
entstand. Da wir genau das verbessern möchten, gehen wir nun anders vor: Wir nehmen die "kleinsten" Bestandteile
des BACnets (Events, Feeds, Datenbanken etc.) als Grundlage und überlegen uns dann, wie wir diese in einem möglichst kompakten
Package organisieren können. Erst wenn wir die Struktur des Cores implementiert haben gehen wir genauer auf die Schnittstellen
zu Applikations- und Transportgruppen ein. So hoffen wir, ein wenig mehr Übersichtlichkeit in das BACnet bringen zu können.  
Ausserdem wurde eine erste Version der Zwischenstandspräsentation erstellt, in der wir unser Projekt genauer vorstellen.



### 10.05.21
Im Meeting wurde nochmals die Themen vom 08.05. aufgenommen und mit allen von uns besprochen, um den genauen Ablauf der nächsten
paar Wochen zu planen. Es wurde somit entschieden, zunächst die Core-Struktur aufzubauen, mit guter Planung und dann auch im Code.
Wir überlegen uns, welche Klassen welche Public-Methoden anbieten müssen und dann bauen wir die interne Struktur auf. Anschliessend
geht es dann um das "Finetuning", wobei die bestehende Struktur erweitert werden kann.  
Ausserdem wurde die Präsentation für den 12.05. fertiggemacht und ein beispielhafter Pythonscript geschrieben, der exemplarisch zeigt,
wie der BACnet Core genutzt werden können soll.



### 12.05.21
Die Präsentation wurde gehalten und die Rückmeldung dazu war hauptsächlich positiv. Im Projekt sollen wir fortan nicht mehr von der
Transport, sondern Replikationsschicht sprechen, um Verwirrung zu vermeiden. Bis am 17.05. soll die API-Spezifikation fertiggestellt
und an alle Teilnehmer der Vorlesung versandt werden, sodass sich andere Gruppen unsere Struktur anschauen können und eventuell noch
Vorschläge / Wünsche abgeben können.  
Die weiteren Arbeiten an einem detaillierten Klassendiagramm wurden begonnen.