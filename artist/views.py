from django.db import connection
import os
import logging
from django.conf import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ArtistSerializer
from user.jwt_utils import decode_jwt_token

logger = logging.getLogger(__name__)

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class ArtistListView(APIView):
    def get(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user or 'error' in user:
            logger.error(f"Token error: {user.get('error')}")
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist")
            artists = dictfetchall(cursor)

        return JsonResponse(artists, safe=False)

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user or 'error' in user:
            logger.error(f"Token error: {user.get('error')}")
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Get user_id from the decoded token (using 'id' as per your jwt_utils)
        user_id = user.get('id')
        if not user_id:
            return JsonResponse({"error": "User ID not found in token"}, status=status.HTTP_401_UNAUTHORIZED)

        data = request.POST.dict()
        image = request.FILES.get("image")

        # Validate serializer
        serializer = ArtistSerializer(data=data)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Handle image upload
        image_url = None
        if image:
            file_path = f"artists/{image.name}"
            saved_path = default_storage.save(file_path, image)
            image_url = default_storage.url(saved_path)

        # Insert into DB
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO artist 
                    (name, dob, address, gender, first_release_year, no_of_albums, user_id, image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        validated_data["name"],
                        validated_data.get("dob"),
                        validated_data.get("address"),
                        validated_data.get("gender"),
                        validated_data.get("first_release_year"),
                        validated_data.get("no_of_albums"),
                        user_id,  # Using the user_id from token
                        image_url
                    ]
                )
                artist_id = cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return JsonResponse({"error": "Database error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"id": artist_id, "image": image_url}, status=status.HTTP_201_CREATED)

class ArtistDetailView(APIView):
    def get(self, request, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist WHERE id = %s", [artist_id])
            artist = dictfetchall(cursor)

        if not artist:
            return JsonResponse({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        return JsonResponse(artist[0])

    def put(self, request, artist_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user or 'error' in user:
            logger.error(f"Token error: {user.get('error')}")
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the artist belongs to the user
        user_id = user.get('id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM artist WHERE id = %s", [artist_id])
            result = cursor.fetchone()
        
        if not result:
            return JsonResponse({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if result[0] != user_id:
            return JsonResponse({"error": "Not authorized to modify this artist"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        image = request.FILES.get("image")

        # Fetch existing artist
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist WHERE id = %s", [artist_id])
            artist = dictfetchall(cursor)

        if not artist:
            return JsonResponse({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)

        # Validate serializer with partial update
        serializer = ArtistSerializer(data=data, partial=True)
        if not serializer.is_valid():
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        # Handle image upload
        image_path = artist[0]["image"]
        if image:
            file_path = f"artists/{image.name}"
            saved_path = default_storage.save(file_path, image)
            image_path = default_storage.url(saved_path)

        # Update DB
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE artist
                    SET name = %s, dob = %s, address = %s, gender = %s, 
                        first_release_year = %s, no_of_albums = %s, image = %s
                    WHERE id = %s
                    """,
                    [
                        validated_data.get("name", artist[0]["name"]),
                        validated_data.get("dob", artist[0]["dob"]),
                        validated_data.get("address", artist[0]["address"]),
                        validated_data.get("gender", artist[0]["gender"]),
                        validated_data.get("first_release_year", artist[0]["first_release_year"]),
                        validated_data.get("no_of_albums", artist[0]["no_of_albums"]),
                        image_path,
                        artist_id,
                    ]
                )
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            return JsonResponse({"error": "Database error: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return JsonResponse({"message": "Artist updated successfully", "image_url": image_path}, status=status.HTTP_200_OK)

    def delete(self, request, artist_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user or 'error' in user:
            logger.error(f"Token error: {user.get('error')}")
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the artist belongs to the user
        user_id = user.get('id')
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id FROM artist WHERE id = %s", [artist_id])
            result = cursor.fetchone()
        
        if not result:
            return JsonResponse({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if result[0] != user_id:
            return JsonResponse({"error": "Not authorized to delete this artist"}, status=status.HTTP_403_FORBIDDEN)

        # Delete artist
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM artist WHERE id = %s", [artist_id])

        return JsonResponse({"message": "Artist deleted successfully"}, status=status.HTTP_200_OK)
class UserArtistsView(APIView):
    def get(self, request, user_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user or 'error' in user:
            logger.error(f"Token error: {user.get('error')}")
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Verify the requesting user has permission (either admin or requesting their own data)
        requesting_user_id = user.get('id')
        if not requesting_user_id:
            return JsonResponse({"error": "User ID not found in token"}, status=status.HTTP_401_UNAUTHORIZED)

        # Allow if admin or requesting their own artists
        is_admin = user.get('role') == 'admin'  # Assuming you have role in your JWT
        if not is_admin and str(requesting_user_id) != str(user_id):
            return JsonResponse({"error": "Not authorized to view these artists"}, status=status.HTTP_403_FORBIDDEN)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist WHERE user_id = %s", [user_id])
            artists = dictfetchall(cursor)

        return JsonResponse(artists, safe=False)