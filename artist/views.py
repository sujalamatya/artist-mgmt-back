from django.db import connection
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ArtistSerializer

def dictfetchall(cursor):
    """Return all rows from a cursor as a list of dictionaries."""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

class ArtistListView(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM artist")
            artists = dictfetchall(cursor)
        serializer = ArtistSerializer(artists, many=True)
        return JsonResponse(serializer.data, safe=False)

    def post(self, request):
        serializer = ArtistSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO artist (name, dob, address, gender, first_release_year, no_of_albums, released)
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
                        # data.get('released', False),
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
                    SET name = %s, dob = %s, address = %s, gender = %s, first_release_year = %s, no_of_albums = %s, released = %s
                    WHERE id = %s
                    """,
                    [
                        data['name'],
                        data.get('dob'),
                        data.get('address'),
                        data.get('gender'),
                        data['first_release_year'],
                        data['no_of_albums'],
                        # data.get('released', False),
                        artist_id,
                    ]
                )
            return JsonResponse({"message": "Artist updated successfully"})
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, artist_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM artist WHERE id = %s", [artist_id])
        return JsonResponse({"message": "Artist deleted successfully"}, status=status.HTTP_204_NO_CONTENT)