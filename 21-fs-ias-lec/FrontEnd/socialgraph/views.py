import json
from pathlib import Path

from django.shortcuts import render
from .models import Nodes, Links
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
    return render(request, 'socialgraph/users.html', context)

def feed(request):
    return render(request, 'socialgraph/feed.html', {'title': 'Feed'})

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})