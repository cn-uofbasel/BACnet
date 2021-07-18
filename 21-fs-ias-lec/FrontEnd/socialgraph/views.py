__author__ = "Philipp Haller, Pascal Kunz, Sebastian Schlachter"

import json
import os
import pathlib
from pathlib import Path
import pdb
import sys

from django.http import HttpResponseRedirect
from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import DetailView

from .importer import create_profiles, create_Recommendations
from .models import Profile, FollowRecommendations
from .utils.jsonUtils import extract_connections, getRoot, getRootFollowsSize, getRootFollowersSize, saveSettings
from django.db.models import F
from django.db.models import Min, Max
import Levenshtein

x = os.getcwd()
from .utils.callToBackend import followCall, unfollowCall, profileUpdateCall

os.chdir(x)

# Create your views here.

path = pathlib.Path('socialgraph/static/socialgraph/')
path2 = path / 'testData.json'
path = path / 'loadedData.json'
# path = path / 'loadedData1.json'

data_file = open(path)
data = json.load(data_file)
data_file.close()

settingsPath = Path('socialgraph/static/socialgraph/')
settingsPath = settingsPath / 'settings.json'
settings_data_file = open(settingsPath)
settings_data = json.load(settings_data_file)
settings_data_file.close()


def home(request):
    x = pathlib.Path(__file__)
    print(x.parent.parent)
    os.chdir(x.parent.parent)
    data_file = open(path)
    data = json.load(data_file)
    data_file.close()
    root = getRoot(data['nodes'])
    follows = getRootFollowsSize(data['links'], root.get("id"))
    followers = getRootFollowersSize(data['links'], root.get("id"))

    settings_data_file = open(settingsPath)
    settings_data = json.load(settings_data_file)
    settings_data_file.close()

    if request.method == "POST":
        response = request.POST['text']
        newSettings = saveSettings(settings_data, response, settingsPath)
        return HttpResponse(newSettings)

    context = {
        'connections': extract_connections(data, "1 1"),
        'root': root,
        'follows': follows,
        'followers': followers,
        'all': len(data['nodes']),
        'activity': root.get("activity level"),
        'influencer': root.get("influencer"),
        'graph': settings_data
    }

    return render(request, 'socialgraph/home.html', context)


def users(request):
    x = pathlib.Path(__file__)
    print(x.parent.parent)
    os.chdir(x.parent.parent)
    data_file = open(path)
    data = json.load(data_file)
    data_file.close()
    root = getRoot(data['nodes'])

    settings_data_file = open(settingsPath)
    settings_data = json.load(settings_data_file)
    settings_data_file.close()

    if request.method == "POST":
        response = request.POST['text']
        j = extract_connections(data, response)
        return HttpResponse(j)

    context = {
        'data': json.dumps(data),
        'root': root,
        'nodes': sorted(data['nodes'], key=lambda item: item["hopLayer"]),
        'links': data['links'],
        'graph': settings_data
    }
    create_profiles(data)
    return render(request, 'socialgraph/users.html', context)


def reloadJson():
    x = pathlib.Path(__file__)
    os.chdir(x.parent.parent)
    data_file = open(path)
    data = json.load(data_file)
    data_file.close()
    return data

"""
Handle UserInputs coming from the Follow / Unfollow GUI.
"""
def follow(request):
    data = reloadJson()
    create_Recommendations(data)
    #Initial QuerySet
    querySetFollow = FollowRecommendations.objects.filter(layer__gte = 2)
    # create a context variable, will be passed to the render of the Follow GUI
    context = {
        'data': json.dumps(data),
        'nodes': data['nodes'],
        'links': data['links'],
        'recommendations': querySetFollow
    }

    # In case we have received an Ajax call from the UI-Layer:
    if request.method == "POST":
        # Get the values of the Ajax call
        response = request.POST.get('text', False)
        mode = request.POST.get('mode', False)
        layer = int(request.POST.get('layer', False))
        influencer = request.POST.get('influencer', False)
        gender = request.POST.get('gender', False)
        ageLower = request.POST.get('ageLower', False)
        ageUpper = request.POST.get('ageUpper', False)
        name = request.POST.get('name', False)
        town = request.POST.get('town', False)

        if (influencer == "false"):
            influencer = "ignore"
        else:
            influencer = True
        #If we are in the follow mode:
        if(mode == "1follow"):
            if layer == 0:
                layer = 1
            query_values = {'layer': layer,
                           'influencer': influencer, 'gender':gender,
                            'age__gte': ageLower, 'age__lte':ageUpper,
                            }
            #Create the arguments for the SQL-Query
            arguments = {}
            for k, v in query_values.items():
                if ((v and v != "all" and v!= "ignore" and v != 1) or (k == 'influencer' and v == True)):
                    arguments[k] = v
            if (layer == 1):
                querySet = FollowRecommendations.objects.filter(**arguments).filter(layer__gte =2)
            else:
                querySet = FollowRecommendations.objects.filter(**arguments)
            #User has reset the filters
            if (response == "reset"):
                querySet = FollowRecommendations.objects.all()
            # User wants to follow another user
            elif (response.startswith("fo")):
                root = getRoot(data['nodes'])
                rootUser = root.get("name")
                rootUserID = root.get("BACnetID")
                followID = str(response[2:18])
                followName = str(response[18:len(response)])
                followCall(mainPersonName=rootUser, mainPersonID=rootUserID, followPersonName=followName,
                           followPersonID=followID)

                data = reloadJson()
                #Update entry in database
                entry = FollowRecommendations.objects.filter(bacnet_id=followID)
                entry.update(layer = 1)
                query_values = {'layer': layer,
                               'influencer': influencer, 'gender': gender,
                               'age__gte': ageLower, 'age__lte': ageUpper,
                               }
                arguments = {}
                for k, v in query_values.items():
                    if ((v and v != "all" and v != "ignore" and v != 1) or (k == 'influencer' and v == True)):
                        arguments[k] = v
                if (layer == 1):
                    querySet = FollowRecommendations.objects.filter(**arguments).filter(layer__gte=2)
                else:
                    querySet = FollowRecommendations.objects.filter(**arguments)
            #Filter with levenshtein if name or town is filled out.
            querySet = filterWithLevenshtein(querySet, name, town)


            text = {
                'data': json.dumps(data),
                'nodes': data['nodes'],
                'links': data['links'],
                'recommendations': querySet
            }

            return render(request, 'socialgraph/FollowBody.html', text)
        #if we are in the unfollow mode
        if (mode == "1unfollow"):
            query_values = {'influencer': influencer, 'gender': gender,
                            'age__gte': ageLower, 'age__lte': ageUpper,
                            }
            arguments = {}
            for k, v in query_values.items():
                if ((v and v != "all" and v != "ignore") or (k == 'influencer' and v == True)):
                    arguments[k] = v
            querySet = FollowRecommendations.objects.filter(**arguments).filter(layer = 1)
            #User has reset the filters
            if (response == "reset"):
                querySet = FollowRecommendations.objects.filter(layer =1)
            # User wants to follow another user
            if (response.startswith("uf")):
                root = getRoot(data['nodes'])
                rootUser = root.get("name")
                rootUserID = root.get("BACnetID")
                unfollowID = str(response[2:18])
                unfollowName = str(response[18:len(response)])
                unfollowCall(mainPersonName=rootUser, mainPersonID=rootUserID, unfollowPersonName=unfollowName,
                             unfollowPersonID=unfollowID)
                data = reloadJson()
                create_Recommendations(data)
                query_values = {'layer': 1, 'influencer': influencer,
                                'gender': gender, 'age__gte': ageLower,
                                'age__lte': ageUpper}
                arguments = {}
                for k, v in query_values.items():
                    if ((v and v != "all" and v != "ignore") or (k == 'influencer' and v == True)):
                        arguments[k] = v
                querySet = FollowRecommendations.objects.filter(**arguments).filter(layer = 1)

            querySet = filterWithLevenshtein(querySet, name, town)

            text = {
                'data': json.dumps(data),
                'nodes': data['nodes'],
                'links': data['links'],
                'recommendations': querySet
            }
            return render(request, 'socialgraph/UnfollowBody.html', text)
    return render(request, 'socialgraph/Follow.html', context)

def addLevenshtein(name, mode):
    if (name == ""):
        return
    if mode == "name":
        for entry in FollowRecommendations.objects.filter():
            entry.levenshteinDistName = Levenshtein.distance(entry.name, name)
            entry.save()
    else:
        for entry in FollowRecommendations.objects.filter():
            entry.levenshteinDistTown = Levenshtein.distance(entry.town, name)
            entry.save()

def filterWithLevenshtein(querySet,name,town):
    addLevenshtein(name, "name")
    addLevenshtein(town, "town")
    minDist = querySet.aggregate(Min('levenshteinDistName'))
    querySet = querySet.filter(levenshteinDistName=minDist.get('levenshteinDistName__min'))
    minDist = querySet.aggregate(Min('levenshteinDistTown'))
    querySet = querySet.filter(levenshteinDistTown=minDist.get('levenshteinDistTown__min'))
    return querySet


def followBody(request):
    return render(request, 'socialgraph/FollowBody.html')


class PostDetailView(DetailView):
    model = Profile


def update_profile(request):

    context = None

    # Change Working directory
    x = pathlib.Path(__file__)
    os.chdir(x.parent.parent)

    # load data from JSON
    fresh_data_file = open(path)
    fresh_data = json.load(fresh_data_file)
    fresh_data_file.close()

    #  get the root node and Profile
    for node in fresh_data['nodes']:
        if node.get('hopLayer') == 0:
            context = {
                'node': node,
                'profile': Profile.objects.filter(myself=True).first()
            }
            break

    if request.method == "POST":  # after 'save' is pressed on update page.
        update = {'BACnetID': node.get('BACnetID')}
        fieldnames = ['gender', 'birthday', 'country', 'town', 'language', 'status']
        # iterate over fieldnames and check if they are contained in the POST and if so, if there value is an update.
        # Add all update values to a hashmap.
        for fn in fieldnames:
            if fn in request.POST:
                if node.get(fn) is not None and node.get(fn) != request.POST[fn] or node.get(fn) is None and \
                        request.POST[fn] != '':
                    if isinstance(request.POST[fn], str):
                        value = request.POST[fn].strip()  # remove dangling spaces
                        update[fn] = value if value != '' else None
                    else:
                        update[fn] = request.POST[fn]
        if 'gender' in update.keys() and update['gender'] == 'other' and request.POST['other'] != '':
            update['gender'] = request.POST['other']  # update of custom gender

        if len(request.FILES) > 0:  # Check if a profile Picture has been uploaded.
            for f in request.FILES.keys():
                profile_pic_path, profile_pic_data = handle_uploaded_file(request.FILES[f], node.get('BACnetID'))
                update['profile_pic'] = profile_pic_path
                update['profile_pic_data'] = profile_pic_data

        root = getRoot(data['nodes'])
        rootUser = root.get("name")
        rootUserID = root.get("BACnetID")

        if len(update) > 1:  # Only make an UpdateCall if there is a real update
            profileUpdateCall(rootUser, rootUserID, update)

        x = pathlib.Path(__file__)  # Change working directory back to Frontend
        os.chdir(x.parent.parent)

        fresh_data_file = open(path)  # Open the new json-file, and create database profiles out of the data.
        fresh_data = json.load(fresh_data_file)
        create_profiles(fresh_data)
        fresh_data_file.close()

        return HttpResponseRedirect(
            "/profile/" + str(node.get('id')))  # after saving redirect the user back to his profile page

    return render(request, 'socialgraph/profile_update.html', context)  # display the update page


def handle_uploaded_file(f, id):
    '''
    Reads the image data from the given File, renames it (according to the id) and stores it on a specific path.

    Parameters
    ----------
    f: the Image File
    id: The BACnetID of the user

    Returns
    -------
    The path to the new Profilepicture
    The data bytes of the Profilepicture
    '''
    path = os.path.join('media', 'profile_pics')
    if not os.path.exists(path):  # Check if directory already there
        os.makedirs(path)  # Else create it
    else:
        for file in os.listdir(path):
            if file.startswith(id):
                os.remove(os.path.join(path, file))  # Delete old profile pictures of this user
    path = os.path.join(path, id + '.' + f.content_type[f.content_type.index('/') + 1:])

    with open(path, 'wb+') as destination:  # Write the image file
        for chunk in f.chunks():
            destination.write(chunk)
        destination.flush()
        os.fsync(destination.fileno())
        destination.close()

    reader = open(path, 'rb')  # read the image bytes, to put them in the pcap-files
    binImage = reader.read()
    reader.close()

    # return the path and the data_bytes
    return os.path.join('profile_pics', id + '.' + f.content_type[f.content_type.index('/') + 1:]), binImage


