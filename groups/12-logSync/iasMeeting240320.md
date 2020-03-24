JOURNAL.MD

IAS Meeting 24.3.20

- Prof Tschudin, (secret) Christopher Sherb, Alexander, Pascal

- Carlos krank

Log:

WIR MACHEN KONKRET EIN SOZIALES NETZ VON EINZELNEN MENSCHEN, und man kann FEEDS subscriben UND IGNORIEREN: TWITTER ohne direkt messages

Wir diskutieren das schichten bild:
- LOG FORMAT, PEER IDs, BLOB OBJS: 
log format - schon vorgegeben, wir machen eine datenbank mit tabellen
peer IDs -
blob objs - können wir ignorieren

ES WERDEN DIE LOG DATENBANKEN NOCH HOCHGELADEN, AN DENEN KANN MAN SICH RICHTEN

GENERELLE FRAGE: wie synced man 2 datenbanken: was hast du, was habe ich, was teilen wir
WAS MÜSSEN WIR AUSTAUSCHEN!
protokoll machen was 2 datenbanken synchronisieren
möglichst effizient (vielleicht durch filterung von feeds(feed von alice interessiert mich, feed von bob nicht))
kein internet, keine IP nummern
1. möglichkeit: LORA!
2. möglichkeit: python schnnittstelle

PYTHON UDP: WIR SIND DER PYTHON KERN 

NICHT TCP sondern UDP!

zuerst mit internet und dann ab mai ohne internet zusammenkoppeln mit den anderen gruppen

GRUPPE 7 LOG STORE GIBT UNS DATENBANKEN

GRUPPE 14 FEED CONTROL GIBT UNS informationen
mich interessieren die feeds von alice und bla, aber nicht von emile und bla bla

INTEGRATIONSPHASE IM MAI

TSCHUDIN IST ON DEMAND für fragen

Es gibt 2 Studenten, A und B, jeder von ihnen besitzt ein Smartphone. Die beiden Studetenten laufen mit den Smartphones offen herum, sodass man QR codes sehen kann. Student A scannt nun den QR code von B. Student A hat einen Filter: Er möchte nur spezifische Daten von Student B. JETZT UNSER TEIL: Wir synchronisieren die beiden Datenbanken A und B, aber nur die "Tabellen" die relevant sind (dh nur die feeds zu den Studenten subscribed sind). 

Unser Ziel wird sein, mit Python 2 Datenbanken effizient zu synchronisieren, dh NICHT GANZE DATENBANKEN ÜBERSCHRIEBEN, sondern irgendwie wissen welche Tabellen an wem geschickt werden müssen. 

TODO:

Carlos informieren

Mit Gruppe 7 treffen

secure scuttlebutt anschauen

Python Standard Library anschauen: Netzwerkprogrammierung UDP, Datenbanken etc