from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='socialgraph-home'),
    path('users/', views.users, name='socialgraph-users'),
    path('about/', views.about, name='socialgraph-about'),
    path('feed/', views.feed, name='socialgraph-feed'),
    path('profile/<pk>/', views.PostDetailView.as_view(), name='profile-detail'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)