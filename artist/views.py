from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ArtistSerializer
from user.jwt_utils import decode_jwt_token

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
        if not user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist")
            artists = dictfetchall(cursor)

        serializer = ArtistSerializer(artists, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)
        if not user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        if user["role"] not in ["artist_manager", "super_admin", "artist"]:
            return JsonResponse({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            user_id = user["user_id"] if user["role"] == "artist" else None  

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO artist (name, dob, address, gender, first_release_year, no_of_albums, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        data['name'],
                        data.get('dob'),
                        data.get('address'),
                        data.get('gender'),
                        data['first_release_year'],
                        data['no_of_albums'],
                        user_id,  
                    ]
                )
                artist_id = cursor.fetchone()[0]
            
            return JsonResponse({"id": artist_id}, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class ArtistDetailView(APIView):
    def get(self, request, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist WHERE id = %s", [artist_id])
            artist = dictfetchall(cursor)
        if not artist:
            return JsonResponse({"error": "Artist not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ArtistSerializer(artist[0])
        return JsonResponse(serializer.data)

    def put(self, request, artist_id):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE artist
                    SET name = %s, dob = %s, address = %s, gender = %s, first_release_year = %s, no_of_albums = %s
                    WHERE id = %s
                    """,
                    [
                        data['name'],
                        data.get('dob'),
                        data.get('address'),
                        data.get('gender'),
                        data['first_release_year'],
                        data['no_of_albums'],
                        artist_id,
                    ]
                )
            return JsonResponse({"message": "Artist updated successfully"})
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM artist WHERE id = %s", [artist_id])
        return JsonResponse({"message": "Artist deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
