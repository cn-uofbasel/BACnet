        WICHTIG ZUM LESE:
Take aways "Plan9: the Use of name spaces":
- two simple ideas: every resource in the system, either local or remote, is represented by a hierarchical file system; and a user or process assembles a private view of the system by constructing a file name space that connects these resources.
- Write a file system protocol which is responsible for finding files (resources) in a hierarchical name tree, attaching to them by name, and accessing their contents by read and write calls. At this level of abstraction, files in Plan 9 are similar to objects, except that files are already provided with naming, access, and protection methods that must be created afresh for objects. given a connection to the root directory of a file server, the Protokol messages navigate the file hierarchy. contains 17 message types: three for initializing and authenticating a connection and fourteen for manipulating objects.
- The auth and attach messages authenticate a connection, established by means outside 9P, and validate its user. The result is an authenticated channel that points to the root of the server. The clone message makes a new channel identical to an existing channel, which may be moved to a file on the server using a walk message to descend each level in the hierarchy. The stat and wstat messages read and write the attributes of the file pointed to by a channel. The open message prepares a channel for subsequent read and write messages to access the contents of the file, while create and remove perform, on the files, the actions implied by their names. The clunk message discards a channel without affecting the file.
- The mount device is the sole bridge between the procedural interface seen by user programs and remote and user-level services. It does all associated marshaling, buffer management, and multiplexing and is the only integral RPC mechanism in Plan 9. The mount device is in effect a proxy object. There is no RPC stub compiler; instead the mount driver and all servers just share a library that packs and unpacks 9P messages.
- Once a day, at 5:00 AM, the file server sweeps through the cache blocks and marks dirty blocks copy-on-write. It creates a copy of the root directory and labels it with the current date, for example 1995/0314. It then starts a background process to copy the dirty blocks to the WORM. The result is that the server retains an image of the file system as it was early each morning. The set of old root directories is accessible using 9P, so a client may examine backup files using ordinary commands. The backup still has protections; it is not possible to subvert security by looking at the backup.
- The process device contains one directory per live local process, named by its numeric process id: /proc/1, /proc/2, etc. Each directory contains a set of files that access the process. For example, in each directory the file mem is an image of the virtual memory of the process that may be read or written for debugging.
- The various services being used by a process are gathered together into the process’s name space, a single rooted hierarchy of file names. When a process forks, the child process shares the name space with the parent. Several system calls manipulate name spaces. Given a file descriptor fd that holds an open communications channel to a service, the call **mount(int fd, char *old, int flags)** authenticates the user and attaches the file tree of the service to the directory named by old. The flags specify how the tree is to be attached to old: replacing the current contents or appearing before or after the current contents of the directory. 
- A directory with several services mounted is called a union directory and is searched in the specified order. The call bind(char *new, char *old, int flags) takes the portion of the existing name space visible at new, either a file or a directory, and makes it also visible at old. For example, **bind("1995/0301/sys/include", "/sys/include", REPLACE)** causes the directory of include files to be overlaid with its contents from the dump on March first.
- Although there is no global name space, for a process to function sensibly the local name spaces must adhere to global conventions. Nonetheless, the use of local name spaces is critical to the system. Both these ideas are illustrated by the use of the name space to handle heterogeneity. 
- The import command connects a piece of name space from a remote system to the local name space. Its implementation is to dial the remote machine and start a process there that serves the remote name space using 9P. It then calls mount to attach the connection to the name space and finally dies; the remote process continues to serve the files. One use is to access devices not available locally. For example, to write a floppy one may say  **import lab.pc /a: /n/dos**   **cp foo /n/dos/bar** The call to import connects the file tree from /a: on the machine lab.pc (which must support 9P) to the local directory /n/dos. Then the file foo can be written to the floppy just by copying it across.


## Erste Besprechung

Wo sollten wir sein in 2 Wochen:

-   linux verzeichniss wo die Hash benannten Dateien drinn sind mit einer ganz einfachen Komando Zeilen Tool bei dem man für einzelne Mockup Dateisysteme abbilden kann.
    
-   Plan 9 konzept verstanden. Plan 9 Art um Namensräume zusammenzustellen: Wie ist es bei uns angekommen?
    
-   Rückmeldung falls unsere Projektideen
    

  

Bemerkungen:

-   Implementierung soll/ kann komplett lokal sein  (es muss kein Netzwerk implementiert werden) → mehrere User auf dem selben Linux System
    
   
    

  

1.  Programm aufrufen
    
2.  Mit dem Server verbinden
    
3.  Shell ähnliche Umgebung in der man Kommandos aufrufen kann (ls, cd, mount, unmount) womit man sich in einem Verzeichnisbaum durcharbeiten kann.
    
4.  mit ‘mount’ soll man externe Namens-Bäume lokal einbinden können
    

	1.  cd in ein bestimmtes directory
    
	2.  ‘mount’ Befehl (innerhalb dieses Directories)
    
	3.  User hat nun einen weiteren Baum (der traversierbar ist mit cd, ls etc.)
    

### Phase 1 (Tool für ein eigenes/ künstliches Dateisystem implementieren)

-   *Mockup Directory*: Python directory als datenstruktur. dieses dann serialisieren und in eine Datei schreiben mit .json. Hinweis: unique element rein machen in ein solches dictionary damit wir keine Kollisionen haben (wenn zufällig 2 leude das gleiche dictionary anlegen und mit dem selben Hash-Wert hinauslaufen).
    
-   Befehle ls, cd, cat (Inhalt von Text Dateien anzeigen) implementieren
    
-   kleiner rudimentärer Kommandozeilen Interpreter der sich in einem Dateibaum kann bewegen.
    
-   ergänzen mit ‘mount’ Befehl um ein anderes/ bereits bestehendes (selber gemachtes) Dateisystem kann einbinden.
    
-   nur eine Person navigiert das ganze bisher
    

Probleme:

-   mount Befehl: man bindet ein Verzeichnis ein dass Namen hat welche mit unseren Kollidieren
    
-   cat Befehl soll die möglichkeit haben auszuwählen, welche dieser 2 kollidierenden readme files man lesen möchte
    
-   cd Befehl ebenso: wenn es zwei unterverzeichnisse hat: in welches Unterverzeichnis möchte ich gehen?
    

→ Paper [Plan9: “the use of namespaces”](http://doc.cat-v.org/plan_9/4th_edition/papers/names)  *das isch nid de glichi link wie de im whatsapp!!! (nur e paar wenigi sitte lang)*

Implementierung konkret:

-   **python directory dass namen der dateien abbildet auf (Hashwert+Zufallszahl). Dieses directory wird auch als directory abgelegt und erhält ebenfalls einen hash wert**. Wenn ein Dateiverzeichnis geändert wird, erzeugt man einen neuen hash wert. D.H. die alten Directories bleiben bestehen und jedes veränderte Directory fliesst zu einem neuen File mit einem neuen Hash wert. Wir verlieren keine Informationen sondern erzeugen immer wieder neue (**append only log**).
    
-   Beliebige Dateien Importieren in das eigene System und diese mit ihrem Hash-Wert ablegen. Das heisst wir haben ein flaches Verzeichnis in dem alle Dateien und Dictionaries. Name = Hashwert der Datei: gleich wie bei IPFS: Ansatz bei dem alle Dateien mit Ihrem intrinsischen Namen (self certified name/ durch die datei definiert) flach in einem Verzeichnis abgelegt sind. die Hierarchie die wir haben wollen ist rein virtuell. Gewisse dieser Dateien beinhalten ein Dictionary bei dem der name “Readme.md” dem Hashwert “XYZ” entspricht. Unser Kommandozeilen-Client kann nachschauen ob die Datei mit diesem Hash-Wert bereits auf dem eigenen System ist. Wenn jemand ‘cat’ aktiviert kann man dies einfach abspielen. Beim Hashwert ist darauf zu achten, dass genügend Zufall drin ist sodass nicht zwei Benutzer ein dictionary anlegen mit dem gleichen Inhalt.
    
-   beim ls befehl braucht es eine Zusatzinformation bei kollisionen: entweder eine Versionsnummer oder ein Finger print mithilfe dem der Benutzer auswählen kann.
    
-   bei einer suche wüden alle Dateien kommen und dann wählt man daraus aus
    
-   Namensräume sind nicht einfach eine Tabelle. Aktive definitionsfrage. Wenn es um ein Directory geht steht drin wo man ein mount machen soll.
    
-   Wenn pro Benutzer ein linux directory zur verfügung steht (mit all den Hash benannten files), dann müssen wir noch eine Konfigurations information haben (wo ist mein root directory) → config.json um den hash wert des root verzeichnisses anzuzeigen. Diese datei ist nicht mit einem Hash benannt sondern ist für alle benutzer steht config.json
    

### Phase 2 (Verzeichnisse werden nun von anderen Leuten zur Verfügung gestellt und verändern sich in der Zwischenzeit)

Probleme:

-   Verzeichnisse werden nun von anderen Leuten zur Verfügung gestellt
    
-   Verzeichnisse verändern sich (in der Zwischenzeit)
    

Implementierung konkret:

-   Annahme: Phase 1 ist fertig und wir haben alle Hash files in einem Linux directory. nun können wir simulieren auf einem PC, dass es einen zweiten Benutzer gibt der sein eigenes linux directory hat.
    
-   **mount befehle machen die in ein anderes linux directory hineinziehen**
    
-   Beispiel: Alice importiert ein Directory von Bob. jedoch ist das von Alice importierte Verzeichnis (von Bob) ein bereits im Vorgang implementiertes Verzeichniss dass Bob von Carol hat. Alice folgt Carol nicht. Alice sieht also diese betreffenden Sachen von Carol nicht. Wir importieren also möglicherweise Dinge auf die Alice gar keinen zugriff hat (Einträge die ins leere Zeigen). Man sieht dann dass es ein Verweis auf den Hash-Wert aber Alice hat die Datei nicht und bei Bob ist sie auch nicht. Da Alice und Carol keine **Follow Beziehung** haben, hat Alice keinen Zugriff auf das Carol Verzeichnis. Dies führt zu Konstellationen bei denen Alice und Bob über ein Verzeichnis reden bei denen nicht der gleiche Inhalt drin ist. → **Dezentrale Problematik** nicht alle haben den gleichen zentral koordinierten Inhalt zur verfügung sondern die persönliche subjektive Sicht auf die Datenwelt.
    
-   Jeder Zustand hat eine Versionsnummer (wie bei Git und Hypercore) die immer weiter ansteigt. man kann auch auf alte Versionen zugreifen.
    
-   **Problematik des refreshes**: wenn Bob gewisse sache nachführt (neues Verzeichnis anlegt in seinem Namensbaum) bekommen wir einen neuen hash wert aber Alice weiss nichts davon. Wir benötigen einen Mechanismus um Alice mitzuteilen, dass es eine neue Version gibt. Auf Github wird das als zentrale Einheit gelöst (man kann schauen was der Head des Masters Branches ist)
    

  

### Phase 3 (Verschlüsselung)

-   Verschlüsselung: Was ist wenn alice und Bob dateien austauschen möchten die gemeinsame schlüssel brauchen: Metadaten werden benötigt die abgelegt sein müssen. Bei einem Import soll direkt so verschlüsselt werden dass sie nur alice und bob lesen können. Fehlermeldung: man kann nur binärcode exportieren aber nicht den Inhalt. public key private key...
    
-   secure sharing:
    

-   alice und bob sind von anfang identifiziert mit dem public key (nicht mit ihrem namen) bekannt sondern
    
-   ist ein directory executable oder nicht (abgebildet indem man es verschlüsselt oder nicht). Nur gewisse leute haben die möglichkeit ein cd in ein directory zu machen.
