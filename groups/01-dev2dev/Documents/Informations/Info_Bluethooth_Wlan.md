# Bluetooth
* #### Informationen:
	* Reichweite bis ca. 100m
	 	| Klasse        | Leistung        |Reichweite  |
	    | ------------- |:-------------:| -------:|
	    | Klasse 1      | 100 mW		  | ca. 100 m|
	    | Klasse 2      | 2,5 mW        | ca. 50 m |
	    | Klasse 3      | 1 mW          | ca. 10 m | => Handy
	* Wlan = max. 2000 mW/ üblicher Heimrouter: 200 mW
	* bis zu 8 Geräte gleihczeitig = Piconet
	* 2,1 Mbit/s Übertragungsgeschwindigkeit(neue Version bis 24 Mbit/s)
	* Wlan über 450 Mbits/s
	* Frequenzbereich 2,402 GHz bis 2,480 GHz

* #### Technologien:
	* ##### GAP (Generic Access Protocol)
		* Used by peripherals
		* Handles connection requests from Centrals
		* Hansles advertisement data
		* Mulitple centrals can read Aavertisement at the same time
	* ##### GATT (Generic Attribute Profile)
		* Used for communication between devices
		* Services are stored in GATT
		* Characteristics stored in services
		* Descriptors
		* Readm Write, Notify
		* Pripherals can only have one connection at a time
	* #### UUIDs (Universally Unique Identifiers)
		* 126-bit

* #### Links
	* [Bluetooth programming in C](https://www.winsocketdotnetworkprogramming.com/winsock2programming/winsock2advancedotherprotocol4p.html)
	* [Bluethooth programming in Python](http://blog.kevindoran.co/bluetooth-programming-with-python-3/)


# WiFi
 * #### Informationen:
 	* Reichweite
 	* Frequentbereich 2,4 GHz & 5GHz
 		* 2400–2483,5 GHz
 			* Leistung 100 mW
 		* 5150–5350 und 5470–5725 GHz
 			* Leistung 200 mW & 1W
 	* IEEE (Institute of Electrical and Electronics´Engineers)
 	  | Bezeichnung        | IEEE Standard        |Maximale Linkrate  |
   	  | ------------- |:-------------:| --------------:|
      | Wi‑Fi 6        | 802.11ax	   | 600–9608 MBit/s| 5 GHz Standard
      | Wi‑Fi 5        | 802.11ac      | 433–6933 MBit/s| 5 GHz Standard
      | Wi‑Fi 4        | 802.11n       | 72–600 MBit/s  | 2,4 GHz & 5 GHz Standard
      | Wi‑Fi 3	       | 802.11g       | 54 MBit/s      | 2,4 GHz Standard
      | Wi‑Fi 2	       | 802.11b       | 11 MBit/s      | 2,4 GHz Standard
      | Wi‑Fi 1	       | 802.11	       | 2 MBit/s       | 2,4 GHz Standard
    * OSI-Referenzmodell (Netzwerkprotokolle als Schichtenarchitektur)
	* Infrastrukturmpdus =>  via Router
	* Ad-Hoc-Modus => peer2peer
		* Alle Stationen benutzen denselben Netzwerknamen („Service Set Identifier“, SSID) und optional dieselben Einstellungen für die Verschlüsselung.
		* koordinierende Funktion von den Endgeräten übernommen werden
		* experimentellen Protokollen (AODV, OLSR, MIT RoofNet, B.A.T.M.A.N. etc.)
		* Standardisierungsvorschlägen (Hybrid Wireless Mesh Protocol, 802.11s)
		* kommerzielle Lösungen (z. B. Adaptive Wireless Path Protocol von Cisco)

* #### Links:
	* [WiFi programming in Pythoon](https://www.youtube.com/watch?v=Lbfe3-v7yE0&t=13s)
	* [WiFi programming in Python](https://www.youtube.com/watch?v=6jteAOmdsYg&list=PLhTjy8cBISErYuLZUvVOYsR1giva2payF)

