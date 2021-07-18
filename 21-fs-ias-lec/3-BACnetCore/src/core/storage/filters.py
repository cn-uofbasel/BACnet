from ..interface.event import Event

"""
This file consists of filters that can be used to filter and search for results on database level. This should give a
performance advantage compared to when you first get all results and filter afterwards.

These filters are standard versions used by the database handler, users can also query events by using filters.
Build your own filters:

1. return functions that take an SQL_Mapped Object like RawEvent
2. The function that is used to filter must return a boolean value
3. use the filter, you can combine filters by creating lambda function that use and concatenate filters
"""


def identifier_is(name: str):
    return lambda event: Event.from_cbor(event.event_as_cbor).content.identifier == name


def identifier_contains(text: str):
    return lambda event: text in Event.from_cbor(event.event_as_cbor).content.identifier


def feed_id_is(identifier: str):
    return lambda event: event.feed_id == identifier
