from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='socialgraph-home'),
    path('about/', views.about, name='socialgraph-about'),
]