import lib.lorasense as lorasense

lorasense = lorasense.LoraSense(mode=0, debug=0)
lorasense.setupLoRa()
lorasense.setupWLAN("CasaSalsi","S@lsi1968")
lorasense.startLoRaComm()