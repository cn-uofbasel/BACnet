import json
from pathlib import Path

from django.shortcuts import render
from django.views.generic import DetailView

from .models import Profile
from .utils.jsonUtils import extract_connections

# Create your views here.

path = Path('socialgraph/static/socialgraph/')
path = path / 'testData.json'
data_file = open(path)
data = json.load(data_file)
data_file.close()


def home(request):

    context = {
        'connections': extract_connections(data)
    }

    return render(request, 'socialgraph/home.html', context)

def users(request):
    #nodes = Nodes()
    #links = Links()

    context = {
        'nodes': data['nodes'],
        'links': data['links'],
        'testChart': 'static/socialgraph/testData.json'
    }
    create_profiles()
    return render(request, 'socialgraph/users.html', context)

def feed(request):
    return render(request, 'socialgraph/feed.html', {'title': 'Feed'})

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})

class PostDetailView(DetailView):
    model = Profile

# Creates Profile Entries in the Database for each Node.
# TODO: Move somewhere else
def create_profiles():
    Profile.objects.all().delete() # Delete all profile entries in the database.
    for node in data['nodes']:
        p = Profile(bacnet_id= node['id'], name= node['name'], gender=node['gender'])
        p.save()
