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
Die weiteren Arbeiten an einem detaillierten Klassendiagramm wurden begonnen. Bis zum nächsten Meeting am 14.05. wird eine geeignete Library
für den Eventbus gesucht und die Anbindung an die Datenbank (SQLite Connector / Storage Connector) genauer untersucht. 



### 15.05.21
Im heutigen Meetings wurde besprochen, welche Bibliothek sich für den Eventbus eignen würde. Nach einiger Recherche haben wir uns provisorisch
auf "pyeventbus3" festgelegt (https://github.com/FlavienVernier/pyeventbus). Diese Library bietet die Möglichkeit, auf einfache Art und Weise
unterschiedliche Events zu erstellen, zu Subscriben, Registrieren und neue Events zu posten etc. Als zentrale Komponente ist dafür der Singleton
PyBus wichtig, auf dem der Eventbus läuft. Ausserdem können für die "Subscribed Methods" verschiedene Modi ausgewählt werden. Man kann die Methoden
zum Beispiel im gleichen Thread wie der Event gepostet wurde laufen lassen oder einen separaten Thread machen. Auch könnte ein neuer Prozess gemacht
werden.  
Auch wurde angesprochen, dass wir wahrscheinlich noch Elemente von LogSync in unser Projekt integrieren müssen. Es geht um die Synchronisation der
Feeds und Events, die ohne solch ein Feature manuell gemacht werden müsste. Dies müsste wahrscheinlich in der "Channel"-Klasse gemacht werden, die 
als Verbindung zur Replikationsschicht dient. Wir würden dort eine Art Protokoll wie im LogSync Projekt machen, dass zum Beispiel den Austausch einer
"I Want" und einer "I Have"-Liste von Feeds definiert. Genaueres wird bis zum nächsten Termin überlegt.



### 15.05.21 - 30.05.21
In dieser Zeit wurde individuell am Projekt gearbeitet. Die Prüfungsvorbereitungen haben es schwer gemacht, regelmässig zusammenzusitzen und mit der Implementation
zu beginnen. Jeder ist nochmals für sich die Struktur des BACnets und des Cores im spezifischen durchgegangen und hat sich nochmals überlegt, ob die
von uns geplante Struktur wirklich am passendsten ist. Die Notizen sollten dann im nächsten Meeting besprochen werden.



### 31.05.21
Die Präsentation für den Mittwoch wurde erstellt. Wir präsentieren den aktuellen Stand unserer Arbeit, also vor allem die finale
Struktur, die wir implementieren möchten. Es wurde ebenfalls nochmals ein Aufruf an alle interessierten Gruppen geplant,  die eventuell
mit uns zusammenarbeiten könnten, um schon in diesem Semester unseren Core zu gebrauchen.



### 02.06.21 - 27.06.21
Die Prüfungen machten es jetzt unmöglich, gross Zeit ins Projekt zu investieren. Wir planten dies jedoch von Beginn weg und hatten schon viel Zeit in
die Planung investiert, wodurch wir nach den Prüfungen dann relativ zügig vorankommen sollten.



### 28.06.21
Es wurde das erste Meeting nach den Prüfungen abgehalten und die grobe Zeitplanung für die Implementierungsphase vorgenommen. Jedes Gruppenmitglied
bekam einen Verantwortungsbereich zugesprochen, in dem in den nächsten Tagen Fortschritt gemacht werden sollte.
Raphael kümmert sich erst einmal um die Implementation der Storage-Control und der Datenbankanbindung und Tim und Nico um
die restliche Architektur, vorerst mal als Skeleton.



### 29.06.21 - 10.07.21
Die im letzten Meeting abgesprochenen Aufgaben wurden erledigt und weiter am Projekt gearbeitet. Tim und Nico haben sich dazu entschlossen, den Eventbus
aus dem Projekt zu streichen und damit einiges an Aufwand zu sparen, der nicht unbedingt nötig ist. Raphael hat unterdessen das Storage Modul
praktisch fertiggestellt.
Es wurde auch eine erste Version der Dokumentation erstellt.



### 11.07.21 - 15.07.21
Die Skeletonmethoden wurden nun implementiert und an der Dokumentation und dem Report gearbeitet. Kleinere Details an der Architektur wurden nochmals
geändert, aber im Grossen und Ganzen blieb unsere Planung relativ gut bestehen.



### 16.07.21
Es wurde nochmals ein Zwischenstandsmeeting mit allen Gruppenmitgliedern abgehalten und die letzten zwei Tage des Projekts wurden
geplant. Dabei geht es primär noch um die Fertigstellung des Reports und das Schreiben von Sample Programmen, einerseits um den Core
zu testen, andererseits um den nächsten Entwicklern des BACnets eine Grundlage zu bieten, anhand der das Verwenden des Cores aufgezeigt wird.
