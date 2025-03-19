from django.urls import path
from .views import MusicListView

urlpatterns = [
    path('songs/', MusicListView.as_view(), name='all-music'),  # Fetch all songs
    path('artists/<int:artist_id>/songs/', MusicListView.as_view(), name='music-list'),  # Fetch songs by artist
]
