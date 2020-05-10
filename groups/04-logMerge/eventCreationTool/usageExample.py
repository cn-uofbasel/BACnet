import EventCreationTool

# LOOK AT THE README THIS FILE IS GOING TO BE THE TESTFILE LATER ON
if __name__ == "__main__":
    ecr = EventCreationTool.EventCreationTool()
    feed_id = ecr.create_feed()
    event = ecr.generate_first_event(feed_id, 'someapp/somecontent', {'somekey': 'somevalue', 'otherkey': 4332})
    second_event = ecr.generate_event_from_previous(event, 'someapp/differentaction', 767)
    print(second_event)
    print(ecr.get_private_key_from_event(event))
    print(ecr.get_private_key_from_feed_id(feed_id))
    print(ecr.get_own_feed_ids())
