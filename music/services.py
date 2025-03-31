# from django.db import connection

# def create_music(artist_id, title, album_name, genre):
#     """Creates a new music entry in the database."""
#     with connection.cursor() as cursor:
#         cursor.execute(
#             """
#             INSERT INTO music (artist_id, title, album_name, genre, created_at, updated_at)
#             VALUES (%s, %s, %s, %s, NOW(), NOW())
#             RETURNING id
#             """,
#             [artist_id, title, album_name, genre]
#         )
#         return cursor.fetchone()[0]

# def delete_music(song_id, artist_id):
#     """Deletes a music entry if it belongs to the specified artist."""
#     with connection.cursor() as cursor:
#         cursor.execute("DELETE FROM music WHERE id = %s AND artist_id = %s", [song_id, artist_id])