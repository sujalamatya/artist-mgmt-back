from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import MusicSerializer

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class MusicListView(APIView):
    def get(self, request, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM music WHERE artist_id = %s", [artist_id])
            songs = dictfetchall(cursor)
        serializer = MusicSerializer(songs, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request, artist_id):
        serializer = MusicSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO music (artist_id, title, album_name, genre)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    [
                        artist_id,
                        data['title'],
                        data.get('album_name'),
                        data['genre'],
                    ]
                )
                song_id = cursor.fetchone()[0]
            return JsonResponse({"id": song_id}, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)