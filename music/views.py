from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MusicSerializer
from user.jwt_utils import decode_jwt_token

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class MusicListView(APIView):
    def get(self, request, artist_id=None):
        # Authenticate the user
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)

        if not user or "id" not in user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user["id"]  # Extract user ID from token
        search_query = request.GET.get("search", "").strip()
        user_music = request.GET.get("user_music")  # Check if user wants their own music
        artist_id = artist_id or request.GET.get("artist_id")

        # Convert artist_id to integer if provided
        try:
            artist_id = int(artist_id) if artist_id else None
        except ValueError:
            return JsonResponse({"error": "Invalid artist_id"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            if user_music:  # Fetch music for the logged-in user's artist profile
                cursor.execute(
                    """
                    SELECT m.* FROM music AS m
                    INNER JOIN artist AS a ON m.artist_id = a.id
                    WHERE a.user_id = %s
                    """,
                    [user_id]
                )
            elif artist_id:  # Fetch music for a specific artist
                cursor.execute("SELECT * FROM music WHERE artist_id = %s", [artist_id])
            else:  # Fetch all music
                cursor.execute("SELECT * FROM music")

            songs = dictfetchall(cursor)

        serializer = MusicSerializer(songs, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, artist_id):
        # Require authentication
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)

        if not user or "id" not in user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        if user["role"] not in ["artist_manager", "super_admin", "artist"]:
            return JsonResponse({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        serializer = MusicSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, NOW(), NOW())
                    RETURNING id
                    """,
                    [
                        artist_id,
                        data["title"],
                        data.get("album_name"),
                        data["genre"],
                    ]
                )
                song_id = cursor.fetchone()[0]
            return JsonResponse({"id": song_id}, status=status.HTTP_201_CREATED)

        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
