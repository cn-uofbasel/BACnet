# Klassenstruktur des BACnet

Dieses Dokument dient dazu, den Entwicklern und anderen Betrachtern eine
Übersicht über den BACnet-Core zu bieten.  
Es werden die einzelnen Klassen des BACnet-Cores und deren Struktur vorgestellt. Im Speziellen
wird auf die nötigen Funktionen eingegangen, die eine Klasse anbieten
muss, um den BACnet-Core zu realisieren.

## Node

Die Node ist die zentrale Klasse des BACnet-Cores.
* Eventbus als Hauptbestandteil



## Storage Connector <abstract>

Der Storage Connector soll als abstrakte Klasse eine modular erweiterbare Anbindung der Nodes an
verschiedene Möglichkeiten zur Speicherung darstellen.  
Als konkrete Implementation liegt der SQLite Connector vor, aber man soll beliebige Datenbankanbindungen
machen können.




## SQLite Connector

Der SQLite Connector dient zur Anbindung an eine SQLite-Datenbank, die als
persistenter Speicher auf den Nodes verwendet werden kann. Die Implementation dazu
stammt aus dem FS20 und die folgende Tabelle beinhaltet die Funktionen der damals geschriebenen
Klasse.  
Die Datenbank beinhaltet eine CBOR Datenbank, Funktionalität für eine Tabelle der
Master Events, sowie auch Funktionalitäten für je eine Tabelle für Kotlin- und Chat-Angelegenheiten.  
Die Kotlin Funktion stammt aus der direkten Anbindung der Kotlin-Chat Gruppe im FS20.

    
| Funktion 	| Parameter   	| Aufgabe  	|
|---	|---	|---	|
| create_cbor_db_tables | - | Erstellen der Tabelle für Events mit den folgenden Rows: ID, Feed ID, Seq Number, Event als CBOR |  
| insert_byte_array | Feed ID, Sequence Number, Event als CBOR | Anhängen eines Events an einen bestehenden Feed | 
|  get_event | Feed ID, Sequence Number | Event getten |
| get_current_seq_number | Feed ID | Aktuelle Sequence Number getten |
| get_current_event_as_cbor | Feed ID | Aktuellster Event als CBOR-File getten |
| get_all_feed_ids | - | Alle Feed IDs der Datenbank als Array getten |
| create_master_table | - | Erstellen der Master-Tabelle mit den folgenden Rows: ID, Master (boolean), Feed ID, App Feed ID, Trust Feed ID, Sequence Number, Trust, Name, Radius, Event as CBOR, App Name |
| insert_master_event | Master, Feed ID, App Feed ID, Trust Feed ID, Sequence Number, Trust, Name, Radius, Event as CBOR, App Name | Erstellen eines neuen Master Events in der Master-Table |
| get_trusted | Master ID | Gibt einen Array mit Feed IDs zurück, denen vertraut wird |
| get_blocked | Master ID | Gibt einen Array mit Feed IDs zurück, die blockiert sind |
| get_all_master_ids | - | Gibt einen Array mit allen Master IDs zurück |
| get_all_master_ids_feed_ids | Master ID | Gibt einen Array mit allen zur Master ID zugehörigen Feed IDs zurück |
| get_username | Master ID | Gibt den Username (Name des Master Events mit entsprechender ID) zurück |
| get_my_last_event | - | Gibt den aktuellsten Event zurück (mit höchster Sequenznummer) |
| get_host_master_id | - | Gibt die Master ID des Hosts zurück (Owner der Node) |
| get_radius | - | Gibt den Radius des Hosts zurück|
| get_master_id_from_feed | Feed ID | Gibt die Master ID des gewünschten Feeds zurück |
| get_application_name | Feed ID | Gibt den Namen der Applikation zurück, auf der der Feed erstellt wurde |
| get_feed_ids_from_application_in_master_id | Master ID, Application Name | Gibt einen Array von Feed IDs zurück, die zu einer bestimmten Applikation und Master ID gehören |
| get_feed_ids_in_radius | - | Explored den eigenen Radius und gibt einen Array von Feed IDs zurück, die darin liegen|
| set_feed_ids_radius | Feed ID, Radius | Aktualisiert den Radius|
| create_kotlin_table | - | Erstellt die Kotlin-Tabelle mit folgenden Rows: ID, Feed ID, Sequence Number, Application, Username, Old Username, Timestamp, Text|
| insert_kotlin_event | Feed ID, Sequence Number, Application, Username, Oldusername, Timestamp, Text | Fügt einen neuen Kotlin Event in einen bestimmten Feed ein |
| get_all_usernames | - | Gibt einen Array von Tuples mit den Usernames und entsprechenden Feed IDs zurück |
| get_all_kotlin_events | - | Gibt eine Liste mit allen Kotlin Events zurück |
| get_all_entries_by_feed_id | Feed ID | Gibt eine Liste von der Feed ID zugehörigen Kotlin Events zurück |
| get_last_kotlin_event | - | Gibt den aktuellsten Kotlin Event zurück |
| create_chat_event_table | - | Erstellt eine neue Chat Event Tabelle mit folgenden Rows: ID, Feed ID, Sequence Number, Application, Chat ID, Timestamp, Chat Message |
| insert_event | Feed ID, Sequence Number, Application, Chat ID, Timestamp, Data | Fügt einen neuen Chat Event an eine Feed ID an |
| get_all_events_since | Application, Timestamp, Chat_id | Gibt eine Liste aller einer Chat ID zugehörigen Events zurück, die aktueller als der mitgegebene Timestamp sind |
| get_all_event_with_chat_id | Application, Chat ID | Gibt eine Liste aller Chat Events zurück, die der mitgegebenen Chat ID angehören |
| session_scope (@contextmanager) | - | Bindet eine Reihe von Datenbank Operationen in einen Transactional Scope ein, schliesst die Session am Schluss |
|||
| **Klasse** | **Parameter** | **Aufgabe** |
| cbor_event | Feed ID, Sequence Number, Event as CBOR | Macht CBOR-Objekte möglich, die in Feeds / CBOR-Tabellen eingefügt werden können |
| chat_event | Feed ID, Sequence Number, Application, Chat ID, Timestamp, Data | Macht Chat-Objekte möglich, die in Feeds / Chat-Tabellen eingefügt werden können |
| kotlin_event | Feed ID, Sequence Number, Application, Username, Oldusername, Timestamp, Text | Macht Kotlin-Objekte möglich, die in Feeds / Kotlin-Tabellen eingefügt werden können |
| master_event | Master, Feed ID, Application Feed ID, Trust Feed ID, Sequence Number, Trust, Name, Radius, Event as CBOR, Application Name | Macht Master-Objekte möglich, die in Feeds / Master-Tabellen eingefügt werden können |
