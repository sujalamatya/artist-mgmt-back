class UserRole:
    SUPER_ADMIN = "super_admin"
    ARTIST_MANAGER = "artist_manager"
    ARTIST = "artist"

    CHOICES = [
        (SUPER_ADMIN, "Super Admin"),
        (ARTIST_MANAGER, "Artist Manager"),
        (ARTIST, "Artist"),
    ]
