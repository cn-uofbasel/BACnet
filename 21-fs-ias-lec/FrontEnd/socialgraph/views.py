import json
from pathlib import Path
import pdb;

from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.generic import DetailView

from .importer import create_profiles, create_Recommendations
from .models import Profile, FollowRecommendations
from .utils.jsonUtils import extract_connections

# Create your views here.

path = Path('socialgraph/static/socialgraph/')
path = path / 'testData.json'
data_file = open(path)
data = json.load(data_file)
data_file.close()


def home(request):

    context = {
        'connections': extract_connections(data, "1 1")
    }

    return render(request, 'socialgraph/home.html', context)

def users(request):

    if request.method == "POST":
        response = request.POST['text']
        j = extract_connections(data, response)
        return HttpResponse(j)

    context = {
        'data': json.dumps(data),
        'nodes': data['nodes'],
        'links': data['links']
    }
    create_profiles(data)
    return render(request, 'socialgraph/users.html', context)

def feed(request):
    return render(request, 'socialgraph/Feed.html', {'title': 'Feed'})

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})

def follow(request):

    recommendationList = []

    for node in data['nodes']:
        if (node.get('hopLayer') < 3):
            recommendationList.append(FollowRecommendations.create(layerNode = node.get('hopLayer'), bacnet_idNode=node.get('id'), nameNode=node.get('name'), genderNode=node.get('gender'),
                            birthdayNode=node.get('birthday'), countryNode=node.get('country'), townNode=node.get('town'),
                            languageNode=node.get('language'),
                            profile_picNode=node.get('profile_pic') if node.get('profile_pic') is not None else 'default.jpg'))
    context = {
        'data': json.dumps(data),
        'nodes': data['nodes'],
        'links': data['links'],
        'recommendations': recommendationList
    }

    if request.method == "POST":
        response = request.POST['text']
        recommendationList = []

        #TODO: nicefy this
        if (response):
            for node in data['nodes']:
                if (node.get('name') == response):
                    recommendationList.append(
                        FollowRecommendations.create(layerNode=node.get('hopLayer'), bacnet_idNode=node.get('id'),
                                                     nameNode=node.get('name'), genderNode=node.get('gender'),
                                                     birthdayNode=node.get('birthday'), countryNode=node.get('country'),
                                                     townNode=node.get('town'),
                                                     languageNode=node.get('language'),
                                                     profile_picNode=node.get('profile_pic') if node.get(
                                                         'profile_pic') is not None else 'default.jpg'))
        else:
            for node in data['nodes']:
                if (node.get('hopLayer') < 3):
                    recommendationList.append(
                        FollowRecommendations.create(layerNode=node.get('hopLayer'), bacnet_idNode=node.get('id'),
                                                     nameNode=node.get('name'), genderNode=node.get('gender'),
                                                     birthdayNode=node.get('birthday'), countryNode=node.get('country'),
                                                     townNode=node.get('town'),
                                                     languageNode=node.get('language'),
                                                     profile_picNode=node.get('profile_pic') if node.get(
                                                         'profile_pic') is not None else 'default.jpg'))



        text = {
            'data': json.dumps(data),
            'nodes': data['nodes'],
            'links': data['links'],
            'recommendations': recommendationList
        }



        return render(request, 'socialgraph/FollowBody.html', text)

    return render(request, 'socialgraph/Follow.html', context)

def followBody(request):
    return render(request, 'socialgraph/FollowBody.html')

class PostDetailView(DetailView):
    model = Profile
