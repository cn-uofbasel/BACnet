# Feed Control

Unsere Gruppe versucht ein Feed Controller einzurichten, mit welchem die Daten gefiltert werden. Dies dient dazu, dass nur Pakete beachtet werden, welche man folgt und dient hoffentlich auch zur Entlastung vom Netz und vom Nutzer.


- Der Nutzer sollte die Möglichkeit haben, anderen Netzwerkteilnehmer zu folgen und deren Feed zu empfangen.
- Ein Feed, dem ein Nutzer folgt, sollte auch empfangen werden. (Wichtig für Chat Applikationen, ansonsten kommt die Hälfte der Nachrichten nicht an.) 
Eine Idee für die Implementation dafür wäre, dass im Log eines Nutzers eingetragen wird, wem der Nutzer folgt und er diese Daten dann auslesen kann, um den im sozialen Radius (z.B. 2 für "Freunde von Freunden") empfangenen Log auch auszulesen.
 - Eine Whitelist, welche dazu verwendet werden kann, zu entscheiden, was man weiter versenden möchte. Da die Bandbreite beschränkt ist, ist es wichtig, dass ein Sensor nur die gewünschten Daten weiter versendet und nicht auch noch die Übertragung von Nutzer Logs tragen muss.
 - Schnittstellen sollten anderen Applikationen Zugriff auf gewisse Funktionen vom Feedmanagement geben, mit der Applikationen z.B. neue Informationen zur Whitelist hinzufügen können. 
 Der Inhalt der Schnittstelle ist noch nicht genau definiert.
- Nutzer können per Button entscheiden, ob sie einem Feed folgen oder nicht mehr folgen möchten. Möglicherweise gibt es dafür eine separate Applikation.

# Onboarding

Das Onboarding ist als separate Applikation zu sehen. Die Applikation soll auf einer Plattform/Gerät lauffähig sein.
