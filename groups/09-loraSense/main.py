import lib.lorasense as lorasense

lorasense = lorasense.LoraSense(mode=1)
lorasense.setupLoRa()

lorasense.startGetInfo()