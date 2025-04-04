from rest_framework import serializers

class MusicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    album_name = serializers.CharField(max_length=255, required=False)
    genre = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)