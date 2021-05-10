# BACNet Core API

Dieses Dokument soll für jede Klasse darstellen, welche öffentlichen Methoden diese unterstützen.
Dadurch soll der komplette Umfang gezeigt werdem, wie man die Bibliothek als normaler Nutzer nutzen kann.
(Modding und Modularität werden separat in anderen Dokumenten erläutert)

## BACNet Node Klasse

Ist die Hauptklasse über welche alle Komponenten der Bibliothek miteinander Kommunizieren.
(Blackboard Architektur) Die Node beinhaltet auch einen Evenbus für diese Kommunikation (Protokoll festlegen?)

### Anforderungen

- Konstruktor zum erstellen komplett neuer Node -> Frisches System ohne Daten
- Konstruktor zum Importieren einer Node -> Erstellen einer Node Aufdrund vorhandener Daten
- Destruktor zum "Herunterfahren der Kommunikation/Node"
- getter für Control-Instanz?
- getter für Feed-Instanzen?
- oder Funktionen direkt anbieten über die Node Klasse?

## Feed Klasse

Repräsentiert einen Feed im BACNet, von einem selbst gespeist oder abbonniert.
Man soll jeden Feed als Instanz/Referenz unabhängig von "Node" Objekt nutzen können
um so zum Beispiel verschiedene Feeds an verschiedene Threads zu geben.

Ein Feed soll keine Daten enthalten, sondern nur metadaten und die Authentifikationsinformation für 
Die Datenbank/Node.

### Abstrakte Anforderungen

- getID      -  
- lastEvent  -
- getContent -

### Anforderungen Owned

- delete - löschen des Eigenen Feeds
- push   -  Einfügen eines Events an den Feed
- hasbeentransmitted - Bool ob die daten schon auf den BACNet sind

### Anforderungen Subscribed

- receive - blocking oder nicht option, fragt ab ob neue Daten für den Feed angekommen sind

### Anforderungen Master

- getUserName
- getSubscribed
- getOwned
- control(ENUM PROTOCOL, params) Protokoll mit welchem die Datenbankinstanz arbeitet bzw alle Komponenten entsprechend reagieren
- getOffered - Liste an feeds welche im Radius verfügbar sind

Protokoll: setRadius, newFeed, deleteFeed, trust/subscribe


## Com-Link

Ist Schnittstelle zum richtigen Netzwerkverkehr, der Com-Link kann in verschiedenen Methoden arbeiten