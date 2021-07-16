# Peer-to-PeerGeocaching App

## Einführung 

Geocacher nennen die Uneingeweihten “Muggel”, wie in der Harry Potter Reihe. Denn im Geocachen weiss man etwas, das die Muggel nicht wissen: fast an jedem öffentlichen Ort der Welt gibt es versteckte Gegenstände, sogenannte “Caches”. Diese sind versteckt, zum Beispiel unter einer Parkbank, hinter einer Werbetafel oder auch in einem kleinen Loch im Boden, dass ein normaler Mensch nur allzu gerne übersieht.

Ein Cache kann verschiedene Formen haben: von einer Zündholzschachtel über eine Filmdose bis hin zur Tupperwarebox oder sogar einer richtigen Truhe! In diesen Caches ist ein Logbuch, in dem man sich einträgt, um zu beweisen, dass man den Cache tatsächlich auch gefunden hat. In manchen dieser Caches gibt es auch eine kleine “Tauschbörse”, nach dem Motto: “Wenn du was hier lässt, kannst du auch gerne etwas mitnehmen”.

Doch wie findet man solche Caches? Geocaching.com hat ein Verzeichnis von abertausenden von Caches, versteckt über die ganze Welt und doch kaum einem Muggel bekannt sind. Mit einem eigenen Account kann man selbst einen Cache verstecken und auf der Webseite hochladen.

Auf einer Karte werden einem dann die ungefähren Positionen der Caches in der Nähe angezeigt. Klickt man auf einen, so erhält man eine Beschreibung. Die Caches können mit genauen Koordinaten versteckt worden sein, mit einem kleinen Rätsel oder sogar mit grossen Rätseln mit mehreren Zwischenlösungen (Multicaches), die einen schlussendlich zur finalen Position des Caches führen.

## Unsere Idee

Um eine künftige Verwirrung zu vermeiden:
Wenn wir von nun an von “Caches” sprechen, dann meinen wir die Information darüber mit den Hinweisen und so weiter, und wenn wir von “physischen Caches” sprechen, dann meinen wir die kleinen Versteckten Dinge in der physischen Welt.

Das Prinzip des Geocachings ist sicher nichts neues, doch haben wir im Rahmen der Vorlesung entdeckt, dass es sehr stark zentralisiert ist. Unser Ansatz ist nun, eine dezentrale Implementation zu finden, bei der sich die Informationen der Caches via Peer-to-Peer-Verbindung (P2P) verbreiten. 
Um es den Leuten so einfach wie möglich zu machen, sich auszutauschen, möchten wir das Geocaching als Android App implementieren.
 
Die App soll die Caches über eine Bluetooth-Verbindung von einem Gerät zum Anderen übertragen.
Auch sollte man in der App seine eigenen Caches erstellen können.

Wenn man einen Cache findet, sollte man diesen in der App lösen können, also sich in die “Hall of Fame” (HoF) eintragen.

Und um den Austausch möglichst zuverlässig zu gestalten, werden die Caches und die HoF-Einträge mithilfe eines Protokolls übertragen, das Secure Scuttlebug sehr ähnlich ist: Hier hat jede Person (Publisher) einen Append-Only Feed, in dem sie neue eigene Caches einträgt sowie bekannt gibt, dass sie einen Cache gelöst hat. Jeder User hat nun die Möglichkeit, die Feeds gewisser Publishers zu abonnieren (subscribe), um deren Feeds zu erhalten.