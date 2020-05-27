from logStore.appconn.kotlin_connection import KotlinFunction
from logStore.funcs.EventCreationTool import EventFactory
import os
import shutil

ecf = EventFactory()
kf = KotlinFunction()

new_event = ecf.next_event('MASTER/MASTER', {})
kf.insert_event(new_event)

feed = EventFactory()
feed2 = EventFactory()
feed3 = EventFactory()

# master feeds
new_event = feed.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

new_event = feed2.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

new_event = feed3.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

# usernames
new_event = feed.next_event('KotlinUI/username',
                            {'newUsername': 'Bob', 'oldUsername': '',
                             'timestamp': 1})
kf.insert_event(new_event)

new_event = feed2.next_event('KotlinUI/username',
                             {'newUsername': 'Alice', 'oldUsername': '', 'timestamp': 2})
kf.insert_event(new_event)

new_event = feed3.next_event('KotlinUI/username',
                             {'newUsername': 'Max', 'oldUsername': '', 'timestamp': 3})
kf.insert_event(new_event)

# feed 1 post
new_event = feed.next_event('KotlinUI/post',
                            {'text': 'Hi Alice, nice to hear from you', 'username': 'Bob',
                             'timestamp': 11})
kf.insert_event(new_event)

# feed 2 post
new_event = feed2.next_event('KotlinUI/post',
                             {'text': 'Hi Bob', 'username': 'Alice', 'timestamp': 15})
kf.insert_event(new_event)

original = '/Users/alex/Code/BACnet/groups/12-logSync/src/udpDir/cborDatabase.sqlite'
target = '/Users/alex/Code/BACnet/groups/12-logSync/src/udpDirSmaller/cborDatabase15.sqlite'
shutil.copyfile(original, target)

original = '/Users/alex/Code/BACnet/groups/12-logSync/src/udpDir/eventDatabase.sqlite'
target = '/Users/alex/Code/BACnet/groups/12-logSync/src/udpDirSmaller/eventDatabase15.sqlite'
shutil.copyfile(original, target)

# feed 3 post
new_event = feed3.next_event('KotlinUI/post',
                             {'text': 'Hello everyone', 'username': 'Max',
                              'timestamp': 17})
kf.insert_event(new_event)

# feed 2 post
new_event = feed2.next_event('KotlinUI/username',
                             {'newUsername': 'Alice2', 'oldUsername': 'Alice', 'timestamp': 20})
kf.insert_event(new_event)

# feed 1 post
new_event = feed.next_event('KotlinUI/post',
                            {'text': 'Gaeb si mir wenigschtens d Vorwau ', 'username': 'Bob',
                             'timestamp': 22})
kf.insert_event(new_event)

# feed 2 post
new_event = feed2.next_event('KotlinUI/post',
                             {'text': 'Per Favore', 'username': 'Alice', 'timestamp': 25})
kf.insert_event(new_event)

# feed 3 post
new_event = feed3.next_event('KotlinUI/post',
                             {'text': 'Nja, ey, Per favore', 'username': 'Max',
                              'timestamp': 28})
kf.insert_event(new_event)

# feed 1 post
new_event = feed.next_event('KotlinUI/post',
                            {'text': 'Oohh, gaeb si mir wenigschtens d Vorwau ', 'username': 'Bob',
                             'timestamp': 32})
kf.insert_event(new_event)

# feed 2 post
new_event = feed2.next_event('KotlinUI/post',
                             {'text': 'De gaebs nume no 10 Millione Kombinatione, ja', 'username': 'Alice', 'timestamp': 36})
kf.insert_event(new_event)

# feed 3 post
new_event = feed3.next_event('KotlinUI/post',
                             {'text': '0-7-9 het sie gseit', 'username': 'Max',
                              'timestamp': 40})
kf.insert_event(new_event)

# feed 1 post
new_event = feed.next_event('KotlinUI/post',
                            {'text': 'Du weisch immerno nuet het si gseit ', 'username': 'Bob',
                             'timestamp': 44})
kf.insert_event(new_event)

# feed 2 post
new_event = feed2.next_event('KotlinUI/post',
                             {'text': 'Nidmau tschuess het sie gseit, ey', 'username': 'Alice', 'timestamp': 48})
kf.insert_event(new_event)


# new key
feed4 = EventFactory()


# new master
new_event = feed4.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

# new username
new_event = feed4.next_event('KotlinUI/username',
                            {'newUsername': 'Alex', 'oldUsername': '',
                             'timestamp': 60})
kf.insert_event(new_event)

# feed 4 post
new_event = feed4.next_event('KotlinUI/post',
                             {'text': 'Und i frage si ob ig ihri - tuet tuet tuet het si gseit', 'username': 'Alex',
                              'timestamp': 62})
kf.insert_event(new_event)

# feed 4 post
new_event = feed4.next_event('KotlinUI/post',
                             {'text': 'yeah', 'username': 'Alex',
                              'timestamp': 64})
kf.insert_event(new_event)

# feed 4 post
new_event = feed4.next_event('KotlinUI/post',
                             {'text': 'I luete jede Tag ar Uskunft aa', 'username': 'Alex',
                              'timestamp': 66})
kf.insert_event(new_event)

# feed 4 post
new_event = feed4.next_event('KotlinUI/post',
                             {'text': 'U moecht ihri Nummer ha', 'username': 'Alex',
                              'timestamp': 66})
kf.insert_event(new_event)
