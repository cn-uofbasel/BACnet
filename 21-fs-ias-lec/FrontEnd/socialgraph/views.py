import json
from pathlib import Path

from django.shortcuts import render
from .models import Nodes, Links

# Create your views here.






def home(request):
    return render(request, 'socialgraph/home.html', {'title': 'Home'})

def users(request):
    #nodes = Nodes()
    #links = Links()

    path = Path('socialgraph/static/socialgraph/')
    path = path / 'testData.json'
    data_file = open(path)
    data = json.load(data_file)
    data_file.close()

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