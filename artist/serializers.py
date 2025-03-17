from rest_framework import serializers

class MusicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    album_name = serializers.CharField(max_length=255, required=False)
    genre = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

class ArtistSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    dob = serializers.DateField(required=False)
    address = serializers.CharField(required=False)
    gender = serializers.CharField(max_length=10, required=False)
    first_release_year = serializers.IntegerField()
    no_of_albums = serializers.IntegerField()
    released = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    songs = MusicSerializer(many=True, read_only=True)  # Nested serializer for songs