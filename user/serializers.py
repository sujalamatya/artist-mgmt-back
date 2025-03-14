from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=255, write_only=True)
    phone = serializers.CharField(max_length=15, allow_blank=True, required=False)
    dob = serializers.DateField(allow_null=True, required=False)
    gender = serializers.CharField(max_length=10, allow_blank=True, required=False)
    address = serializers.CharField(allow_blank=True, required=False)
    role = serializers.ChoiceField(choices=['super_admin', 'artist_manager', 'artist'])