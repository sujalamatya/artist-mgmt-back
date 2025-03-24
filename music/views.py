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

        user_id = user["id"] 
        search_query = request.GET.get("search", "").strip()
        user_music = request.GET.get("user_music")  # Check if user wants their own music
        artist_id = artist_id or request.GET.get("artist_id")

        try:
            artist_id = int(artist_id) if artist_id else None
        except ValueError:
            return JsonResponse({"error": "Invalid artist_id"}, status=status.HTTP_400_BAD_REQUEST)

        query = "SELECT m.* FROM music AS m"

        # condition for filtering by artist if user_music is provided
        if user_music:
            query += """
                INNER JOIN artist AS a ON m.artist_id = a.id
                WHERE a.user_id = %s
            """
            params = [user_id]
        elif artist_id:
            query += " WHERE artist_id = %s"
            params = [artist_id]
        else:
            params = []

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            songs = dictfetchall(cursor)

        #  search filtering
        if search_query:
            search_query = search_query.lower()
            songs = [
                song for song in songs
                if search_query in song["title"].lower() or
                   search_query in (song.get("album_name") or "").lower() or
                   search_query in song["genre"].lower()
            ]

        serializer = MusicSerializer(songs, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)

        if not user or "id" not in user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user["id"]

        if user["role"] not in ["artist_manager", "super_admin", "artist"]:
            return JsonResponse({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        # Fetch artist_id for the logged-in user
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM artist WHERE user_id = %s", [user_id])
            artist = cursor.fetchone()

        if not artist:
            return JsonResponse({"error": "No associated artist found for this user"}, status=status.HTTP_403_FORBIDDEN)

        artist_id = artist[0]  # Extract artist_id from the query result

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

    def delete(self, request, song_id):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JsonResponse({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        user = decode_jwt_token(token)

        if not user or "id" not in user:
            return JsonResponse({"error": "Invalid or expired token"}, status=status.HTTP_401_UNAUTHORIZED)

        user_id = user["id"]

        # artist_id of the logged-in user
        with connection.cursor() as cursor:
            cursor.execute("SELECT id FROM artist WHERE user_id = %s", [user_id])
            artist = cursor.fetchone()

        if not artist:
            return JsonResponse({"error": "No associated artist found for this user"}, status=status.HTTP_403_FORBIDDEN)

        artist_id = artist[0]  

        # Check if the music exists and belongs to the logged-in artist
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM music WHERE id = %s AND artist_id = %s", [song_id, artist_id]
            )
            music = cursor.fetchone()

        if not music:
            return JsonResponse({"error": "Music not found or you do not have permission to delete it"}, status=status.HTTP_404_NOT_FOUND)

        # Delete music
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM music WHERE id = %s", [song_id])

        return JsonResponse({"message": "Music deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
