
from django.urls import path
from .views import ArtistListView, ArtistDetailView

urlpatterns = [
    path("artists/", ArtistListView.as_view(), name="artist_list"),
    path("artists/<int:artist_id>/", ArtistDetailView.as_view(), name="artist_detail"),
]

