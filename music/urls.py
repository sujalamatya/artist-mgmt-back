from django.urls import path
from .views import MusicListView

urlpatterns = [
    path('songs/', MusicListView.as_view(), name='all-music'),  # Fetch all songs
    path('artist/songs/', MusicListView.as_view(), name='user-music'),  # Fetch logged-in user's music
    path('artists/<int:artist_id>/songs/', MusicListView.as_view(), name='music-list'),  # Fetch music by artist ID
     path('songs/<int:song_id>/', MusicListView.as_view(), name='delete-music'),
]
