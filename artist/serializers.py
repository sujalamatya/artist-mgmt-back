from rest_framework import serializers

class ArtistSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    dob = serializers.DateField(required=False)
    address = serializers.CharField(required=False)
    gender = serializers.CharField(max_length=10, required=False)
    first_release_year = serializers.IntegerField()
    no_of_albums = serializers.IntegerField()
    # released = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)