# Feed Control

Unsere Gruppe versucht ein Feed Controller einzurichten, mit welchem die Daten gefilltert werden. Dies dient dazu, dass nur Pakete beachtet werden, welche man folgt und dient hoffentlich auch zur entlasstung vom Netz und vom Nutzer.


- Der Nutzer sollte die Möglichkeit haben, anderen Netzwerkteilnehmer zu folgen und deren Feed zu empfangen.
- Der Feed welcher ein Nutzer dem man folgt sollte auch empfangen werden. (Wichtig für Chat Applikationen, ansonsten bekommt die hälfte der Nachrichten nicht mit. 
Eine Idee für die Implementation dafür wäre, dass im Log eines nutzer eingetragen wird, wenn man jemandem folgt und diese Daten dann auslesen kann, um den im Radius 2 empfangten Log auch auszulesen.
 - Eine Whitelist, welche dazu verwendet werden kann, zu entscheiden was man weiter versenden möchte. Da die Bandbreite beschränkt ist, ist es wichtig, dass ein Sensor nur die gewünschten Daten weiter versendet und nicht auch noch die übertragung von nutzer Logs tragen muss.
 - Schnittstellen sollten anderen Applikationen zugriff auf gewisse Funktionen vom Feedmanagement geben, mit der Applikationen z.B. neue Informationen zur Whitelist hinzufügen können. 
 Der Inhalt der Schnitstelle ist noch nicht genau definiert.
