# Plenum Diskussion
Ziel: Kommandozeilen-Programm (mount/ls/cd)

Ausgangspunkt:

1.  Wir haben ein persönliches Dateisystem (Projekt 1 / Mockup)
    
2.  andere Personen möchten Ihre eigenen persönlichen Dateisysteme mit mir teilen
    

Aufgabe:

...diese n Dateisysteme sollen mit dem Kommando ‘mount’ zu einem Dateisystem zusammengefasst werden (Übergelagerte Zusammenfassung von mehreren Dateisystemen zu einem einheitlichen Dateisystem)

Probleme:

-   Namenskollisionen:
    

-   Ich mache einen ‘mount’ an einem bestimmten Ort aber es befinden sich dort mehrere Dateien mit selbem Namen.
    

-   Plan9 Lösung: Union Dictionaries: Fusionieren solcher Verzeichnisse durch Exponieren. Es gibt nicht eine Wahrheit sondern mehrere.
    

Fragestellungen:

-   Was sind die Konsequenzen davon?
    
-   Problem: gewisse Leute sehen nicht alles
    
-   Kann man ein solches gemergtes Dateisystem wiederum exportieren an andere?
    

Kommunikation:

“Die Kommunikationsbeziehung zwischen zwei Plan9 Knoten soll über Python Module hin durchgeschleift werden welche das abbilden auf Append-Only-Logs im Linux Bereich.”
