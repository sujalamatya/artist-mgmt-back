from django.urls import path
from .views import MusicListView

urlpatterns = [
    path('artists/<int:artist_id>/songs/', MusicListView.as_view(), name='music-list'),
]