from django.shortcuts import render
from .models import Nodes

# Create your views here.




links = [
    {
        "source": 1,
        "target": 2
    },
    {
        "source": 1,
        "target": 5
    },
    {
        "source": 1,
        "target": 6
    },
    {
        "source": 2,
        "target": 3
    },
    {
        "source": 2,
        "target": 7
    },
    {
        "source": 3,
        "target": 4
    },
    {
        "source": 8,
        "target": 3
    },
    {
        "source": 4,
        "target": 5
    },
    {
        "source": 4,
        "target": 9
    },
    {
        "source": 5,
        "target": 10
    },
    {
        "source": 1,
        "target": 11
    },
    {
        "source": 4,
        "target": 12
    },
    {
        "source": 12,
        "target": 13
    },
    {
        "source": 8,
        "target": 14
    },
    {
        "source": 3,
        "target": 15
    },
    {
        "source": 2,
        "target": 16
    }
  ]


def home(request):
    return render(request, 'socialgraph/home.html', {'title': 'Home'})

def users(request):
    nodes = Nodes()

    context = {
        'nodes': nodes.create(),
        'links': links,
        'testChart': 'static/socialgraph/testData.json'
    }
    return render(request, 'socialgraph/users.html', context)

def about(request):
    return render(request, 'socialgraph/about.html', {'title': 'About'})