from src.logStore.appconn.kotlin_connection import KotlinFunction
from src.logStore.funcs.EventCreationTool import EventFactory

ecf = EventFactory()
kf = KotlinFunction()

new_event = ecf.next_event('MASTER/MASTER', {})
kf.insert_event(new_event)

feed = EventFactory()
feed2 = EventFactory()
feed3 = EventFactory()

new_event = feed.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

new_event = feed2.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

new_event = feed3.next_event('KotlinUI/MASTER', {'master_feed': ecf.get_feed_id()})
kf.insert_event(new_event)

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

"""
new_event = feed.next_event('KotlinUI/post',
                            {'text': 'Hi Alice, nice to hear from you', 'username': 'Bob',
                             'timestamp': 11})
kf.insert_event(new_event)

new_event = feed2.next_event('KotlinUI/post',
                             {'text': 'Hi Bob', 'username': 'Alice', 'timestamp': 15})
kf.insert_event(new_event)

new_event = feed3.next_event('KotlinUI/post',
                             {'text': 'Hello everyone', 'username': 'Max',
                              'timestamp': 17})
kf.insert_event(new_event)

new_event = feed2.next_event('KotlinUI/username',
                             {'newUsername': 'Alice2', 'oldUsername': 'Alice', 'timestamp': 20})
kf.insert_event(new_event)
"""