import json
from pathlib import Path

from django.shortcuts import HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView

from .importer import create_profiles
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
        'connections': extract_connections(data, 1)
    }

    return render(request, 'socialgraph/home.html', context)

def users(request):
    #nodes = Nodes()
    #links = Links()

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
    return render(request, 'socialgraph/feed.html', {'title': 'Feed'})

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})

class PostDetailView(DetailView):
    model = Profile
