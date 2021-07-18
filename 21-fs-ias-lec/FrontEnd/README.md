# BACNet FrontEnd

## Einführung

Im Rahmen des Projektes in der Vorlesung Internet and Security stellten wir uns die Aufgabe das Frontend
des sozialen Graphen vom BACnet zu implementieren. Die Visualisierung des Netzwerks in Form eines gerichteten Graphen steht dabei im Zentrum, jedoch soll das Frontend den Nutzern auch weitere Funktionalitäten
zur Verfugung stellen. Dazu zählen hauptsächlich das Folgen und Entfolgen von Personen, sowie das Updaten
der eigenen Nutzerinformationen. Die Möglichkeit das Look and Feel und die Werte der Graph-Attribute anpassen zu können, soll es den Nutzern ferner erlauben, das Aussehen des Frontends nach eigenem Geschmack
anzupassen.


## Setup
Um die nötigen Dependencies wie beispielsweise das Django-Framework zu installieren, haben wir ein Skript programmiert. Es befindet sich im Ordner ’FrontEnd’. Folgender Befehl installiert alle Dependencies:
```
python setup.py install
```

Um das FrontEnd zu laufen zu bringen, sind nun folgende weitere Schritte notwendig:
1. Man lässt das main-Programm vom BackEnd laufen. So werden die PCAP files und das JSON-File erstellt.
2. Man manövriert zum Ordner ’FrontEnd’ in welchem sich das File manage.py befindet
3. Man führt folgenden Befehl aus: ```python manage.py makemigrations``` So wird sichergestellt, dass
Veränderungen die am Model vorgenommen wurden, für das Migrieren in die Datenbank bereit gemacht
werden.
4. Anschliessend: ```python manage.py migrate``` So werden Veränderungen an der Datenbank angewandt.
5. Der Server kann nun gestartet werden mit: ```python manage.py runserver```. Der Server l¨auft anschliessend
auf dem Localhost.


