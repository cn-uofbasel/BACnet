# BacnetEchoClient

# import feed

outgoing = feed.FEED('outgoing.pcap')
incoming = feed.FEED('incoming.pcap')

echo = BACNETTCP('outgoing.pcap', 'incoming.pcap')
echo.open('buerkl.in', 22013)

echo.wr('zeile eins')
echo.wr('zeile zwei')
print(echo.rd())
print(echo.rd())

echo.close()

# eof
