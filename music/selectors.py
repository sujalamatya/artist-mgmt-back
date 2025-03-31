# from django.db import connection
# from music.utils import dictfetchall

# def get_music_list(user_id=None, artist_id=None):
#     """Fetches music list with optional filters for user or artist."""
#     query = "SELECT m.* FROM music AS m"
#     params = []

#     if user_id:
#         query += " INNER JOIN artist AS a ON m.artist_id = a.id WHERE a.user_id = %s"
#         params.append(user_id)
#     elif artist_id:
#         query += " WHERE artist_id = %s"
#         params.append(artist_id)

#     with connection.cursor() as cursor:
#         cursor.execute(query, params)
#         return dictfetchall(cursor)

# def get_artist_by_user(user_id):
#     """Fetch artist ID by user ID."""
#     with connection.cursor() as cursor:
#         cursor.execute("SELECT id FROM artist WHERE user_id = %s", [user_id])
#         return cursor.fetchone()
