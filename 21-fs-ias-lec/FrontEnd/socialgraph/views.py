from django.shortcuts import render
from .models import Nodes, Links

# Create your views here.






def home(request):
    return render(request, 'socialgraph/home.html', {'title': 'Home'})

def users(request):
    nodes = Nodes()
    links = Links()

    context = {
        'nodes': nodes.create(),
        'links': links.create(),
        'testChart': 'static/socialgraph/testData.json'
    }
    return render(request, 'socialgraph/users.html', context)

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})

def feed(request):
    return render(request, 'socialgraph/feed.html', {'title': 'Feed'})