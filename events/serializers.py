from rest_framework import serializers

class EventSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    artist_id = serializers.IntegerField()
    user_id = serializers.IntegerField(allow_null=True, required=False)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(allow_blank=True, required=False)
    event_date = serializers.DateTimeField()
    location = serializers.CharField(max_length=255, allow_blank=True, required=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)