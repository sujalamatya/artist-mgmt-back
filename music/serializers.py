from rest_framework import serializers

class MusicSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField(read_only=True)  # Read-only because it will be set automatically
    title = serializers.CharField(max_length=255)
    album_name = serializers.CharField(max_length=255, required=False)
    genre = serializers.CharField(max_length=50)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def create(self, validated_data):
        # Automatically assign artist_id from the logged-in user
        user = self.context['request'].user  # Get the logged-in user
        validated_data['artist_id'] = user.id  # Set artist_id from the logged-in user's ID
        return super().create(validated_data)