# I&S Security Gruppe 1 - AirDrop

## Content

*   [AirDrop](#airdrop)
*   [How it works](#how-it-works)
*   [Nice-to-look-into alternatives](#nice-to-look-into)
*   [Glossary](#glossary)
*   [Links](#link)

## AirDrop

*   priorietary ad-service
*   uses:

*   [Bluetooth](https://en.wikipedia.org/wiki/Bluetooth) or [Bluetooth Low Energy(?)](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy)
*   Wi-Fi (both devices aren't required to be connected to the same Wi-Fi network (?))
*   Other underlying technologies that are used (and should be investigated/understood) are [Bonjour](#bonjour), [AWDL](#AWDL)

## How it works

*   AirDrop uses [TLS encryption](https://en.wikipedia.org/wiki/Transport_Layer_Security) over a direct Apple-created <a href="">peer-to-peer</a> <a href="">WiFi</a> connection
*   The Wi-Fi radios of both sides communicate directly without using an Internet connection or Wi-Fi Access Point (?)
*   in some way not known yet, it also uses [Bonjour](https://en.wikipedia.org/wiki/Bonjour_(software))
*   !If possible we need to test these claims!

## Nice-to-look-into alternatives

*   (Android Beam, similar tech for Android, [NFC](https://en.wikipedia.org/wiki/Near-field_communication) based)
*   Shoutr, a free P2P multi-user solution
*   [WiFi Direct](https://en.wikipedia.org/wiki/Wi-Fi_Direct), a similar technology
*   Zapya, a free file transfer solution over Wi-Fi

## Glossary

*   [wireless ad hoc network(WANET)/mobile ad hoc network(MANET)](https://en.wikipedia.org/wiki/Wireless_ad_hoc_network#Wireless_sensor_networks)

*   decentralized type of wireless network
*   does not rely on prexisting infrastructure(routers/access points)
*   each node participates in routing by forwarding data for other nodes
*   determination of which nodes forward data is made dynamically on the basis of network connectivity (and the routing algorithm in use)

*   [Apple Wireless Direct Link (AWDL)](https://owlink.org/wiki/)

*   successor to the unsuccessful Wi-Fi IBSS a.k.a ad hoc mode and Apple's competitor to Wi-Fi Direct, now adopted by the Wi-Fi Alliance
*   Function:

*   each AWDL node announces a sequence of Availability Windows (AWs) indicating its readiness to communicate with other AWDL nodes.
*   An elected master node syncronizes these sequences

*   used by other sercies like Auto Unlock, CarPlay
*   Link: [Wireshark dissector for AWDL](https://github.com/seemoo-lab/wireshark-awdl)
*   There are already open source implementations like OWL and OpenDrop

*   [TLS encryption](https://en.wikipedia.org/wiki/Transport_Layer_Security)
*   [Bonjour](https://en.wikipedia.org/wiki/Bonjour_(software)), Apple's implementation of zero-configuration networking(zeroconf)
    *   the service discovery protocol employed in AirDrop

## Test of Discovery/Bonjour Browser

Discovery (used to be called Bonjour Browser) is a mac app which displays all services declared using Bonjour
![stat1](https://github.com/TK5-Tim/FreedomDrop/blob/master/Screenshot%202020-03-17%20at%2000.54.55.png)
![stat2](https://github.com/TK5-Tim/FreedomDrop/blob/master/Screenshot%202020-03-17%20at%2000.54.47.png)
![stat3](https://github.com/TK5-Tim/FreedomDrop/blob/master/Screenshot%202020-03-17%20at%2000.54.26.png)
## Links:

*   [GitHub Repo](#) for stuff
*   Keynote: [How AWDL Works](https://youtu.be/gr7ZOHxGLpI?t=1306)
*   Paper: [Cross-Platform Ad hoc Communication with Apple Wireless Direct Link](https://arxiv.org/pdf/1812.06743.pdf)
*   Paper: [User Manual for the Apple CoreCapture Framework](https://arxiv.org/pdf/1808.07353.pdf)
*   https://en.wikipedia.org/wiki/AirDrop
*   https://en.wikipedia.org/wiki/Wireless_ad_hoc_network#Wireless_sensor_networks
*   https://en.wikipedia.org/wiki/Near-field_communication
*   https://owlink.org/wiki/
*   https://github.com/seemoo-lab/wireshark-awdl
*   https://en.wikipedia.org/wiki/Bonjour_(software)
*   https://en.wikipedia.org/wiki/Wi-Fi_Direct
*   https://en.wikipedia.org/wiki/Bluetooth
*   https://en.wikipedia.org/wiki/Bluetooth_Low_Energy
