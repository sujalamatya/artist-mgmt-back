from rest_framework import serializers
from django.core.files.uploadedfile import InMemoryUploadedFile

class ArtistSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)  
    name = serializers.CharField(max_length=255)
    dob = serializers.DateField()
    address = serializers.CharField(max_length=255)
    gender = serializers.CharField(max_length=10)
    first_release_year = serializers.IntegerField()
    no_of_albums = serializers.IntegerField()
    image = serializers.ImageField(required=False)  # Accept file upload

    def validate_image(self, value):
        if isinstance(value, InMemoryUploadedFile):
            return value  # Valid file
        raise serializers.ValidationError("Invalid image format.")