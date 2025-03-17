from django.urls import path
from .views import ArtistListView, ArtistDetailView, MusicListView

urlpatterns = [
    path('artists/', ArtistListView.as_view(), name='artist-list'),
    path('artists/<int:artist_id>/', ArtistDetailView.as_view(), name='artist-detail'),
    path('artists/<int:artist_id>/songs/', MusicListView.as_view(), name='music-list'),
]