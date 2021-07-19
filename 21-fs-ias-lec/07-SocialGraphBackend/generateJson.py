__author__ = "Philipp Haller, Pascal Kunz, Sebastian Schlachter"

import json
import sys

import os
from pathlib import Path


def generate_json(person_list, we_are):  # Assumption that we have a follow list of each person in the given list
    """
    Writes all the attributes of all Persons in the list in a JSON-file.
    The file has to main components:
    1. A list of nodes that contains all a nodes data and attributes.
    2. A list of links that define the connections within the network graph.

    Parameters
    ----------
    person_list: List of all persons in the network part that is visible to the user
    we_are: The Person instance that corresponds to the user

    Returns
    -------
    A String that contains all the data the Frontend needs, in a serialized format.
    """
    links = []
    nodes = []
    nodeIDs = {}

    for i in range(0, len(person_list)):
        person = person_list[i]
        curBACnetID = person.id
        nodeIDs[curBACnetID] = i  # create a mapping from the BACnetID to the ID used in the Frontend Graph

    ourID = 0
    for i in range(0, len(person_list)):
        person = person_list[i]
        if person == we_are:
            ourID = i  # Get the ID of the current user.
        node = {}
        followList = person.get_follow_list()
        # Store all attributes of a person in the node hashmap...
        if sys.platform.startswith("linux"):  # compatibility for all operating systems
            node['BACnetID'] = person.id
        else:
            node['BACnetID'] = person.id.decode("utf-8")
        node['id'] = nodeIDs[person.id]  # .decode("utf-8")]
        node['name'] = person.name
        node['gender'] = person.gender
        node['birthday'] = person.birthday
        node['country'] = person.country
        node['town'] = person.town
        node['language'] = person.language
        node['status'] = person.status
        node['status_list'] = person.status_list
        node['activity level'] = person.get_activity()
        node['influencer'] = person.influencer
        node['hopLayer'] = 10000
        node['profile_pic'] = person.profile_pic
        nodes.append(node)  # add the current node to the list
        for friend in followList:  # iterate through the follow list and create corresponding links.
            link = {'source': node['id'],
                    'target': nodeIDs[friend]}  # .decode("utf-8")]}
            links.append(link)

        # TODO: In the future refreshes Profilepics.
        # if person.profile_pic is not None:
        #    person.feed.load_profile_pic(person.profile_pic)

    #  Trigger the hopLayer calculation for all nodes.
    calculate_hops(ourID, links, nodes)

    data = {'nodes': nodes, 'links': links}

    path = Path('socialgraph/static/socialgraph/')
    path = path / 'loadedData.json'
    # for testing: path = path / 'loadedData1.json'

    # Change working directory to Frontend
    backEnd = os.getcwd()
    # If we called the callToBackEnd function from the Frontend:
    if (backEnd.endswith("21-fs-ias-lec")):
        os.chdir("07-BackEnd")
        backEnd = os.getcwd()
    frontEnd = backEnd.replace("07-BackEnd", "FrontEnd")
    os.chdir(frontEnd)

    # Write file
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'w') as json_file:
        json.dump(data, json_file, indent=2)

    # Change back the working directory
    os.chdir(backEnd)

    return json.dumps(data)


def calculate_hops(root_id, links, nodes):  # Calculates the hop layer of each node iteratively
    """
    Calculates the hoplayer for each node.
    This number corresponds to the amount of links that have to be traversed to reach a node, starting at the root.
    Bellman-Ford algorithm is used.

    Parameters
    ----------
    root_id: The id used by the Frontend that belongs to the root (the current users node).
    links: List of all links in the network graph part that is visible to the user.
    nodes: List of all nodes that are visible to the user

    Returns
    -------
    """
    distances = []
    for node in nodes:
        distances.append(10000)  # Init all distances to "infinity"

    oldDistances = distances.copy()
    distances[root_id] = 0  # set the roots distance to zero
    while distances != oldDistances:  # iterate until nothing changes
        oldDistances = distances.copy()
        for link in links:  # iterate through links, and update there distances to the root
            if distances[link['source']] + 1 < distances[link['target']]:
                distances[link['target']] = distances[link['source']] + 1

    for node in nodes:  # store the distances in each nodes hopLayer field.
        node['hopLayer'] = distances[node['id']]
