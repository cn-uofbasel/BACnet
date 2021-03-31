# I&S Security Gruppe 1 - dev2dev

## Content

* [Contributors](#contributors)
* [Code](#code)
* [Documents](#documents)
    * [Graphs](#graphs)
    * [Informations](#informations)
    * [Journals](#journals)
    * [Presentations](#presentations)
* [Ressources](#ressources)

## Contributors

Mateusz Palasz ([@MateuszPalasz](https://github.com/MateuszPalasz))
Oliver Weinmeier ([@oliverweinm](https://github.com/oliverweinm))
Tim Keller ([@TK5-Tim](https://github.com/TK5-Tim))

## Code 
Includes two different versions of our project:
* [BTonly](Code/BTonly) has the code for the independent application for updating pcap files.
* [application](Code/application) has the code for the connected application to logMerge and feedControl

## Installation Dependencies
the following dependencies are needed for the use of our program:
* MacOS 10.15 Catalina 
* cbor2 (pip3 install cbor2)
* pybluez 0.30 build by tigerking on Github ( https://github.com/tigerking/pybluez/releases )


## Documents
### Graphs 
![Big Picture](Documents/Graphs/Gesamtbild.png)
This picture shows the main parts of the project fit into the big Picture of the whole project.  

![Workflow Log Exchange](Documents/Graphs/Workflow_Log_Exchange.png)
Flow Diagram to show how two Peers exchange logs to be synchronized.
### Informations 
All the Research made for the project is documentated in there: 
[Research Informations](Documents/Informations/ResearchInformations.md)

### Journals 
Journals of all meetings that took place:  
* [Journal Meeting 24.03.2020](Documents/Journals/Journal_Meeting_20_03_24.md)
* [Journal Meeting 14.04.2020](Documents/Journals/Journal_Meeting_20_04_14.md)
* [Journal Meeting 15.04.2020](Documents/Journals/Journal_Meeting_20_04_15.md)
* [Journal Meeting 20.04.2020](Documents/Journals/Journal_Meeting_20_04_20.md)
* [Journal Meeting 06.05.2020](Documents/Journals/Journal_Meeting_20_05_06.md)
* [Journal Meeting 19.05.2020](Documents/Journals/Journal_Meeting_20_05_19.md)

### Presentations
* [Status Präsentation 16.04.2020](Documents/Presentations/Status/Status_presentation.pptx)

### TO-DO
- [x] Anleitung für @tschudin, um das Problem zu reproduzieren
- [x] Disconnect Funktion
- [x] leere PCAP handeln
- [x] PCAP Format kompatibel (Tschudin Mail)
- [x] Verarbeitung von mehreren Pcap Files
- [x] Schnittstellen Gruppe 4 andocken
	* Funktionen ersetzen
- [x] Testen Demo / Demo aufsezten

## Ressources 
All Ressources that might be Helpful for the project are stored in there. 
