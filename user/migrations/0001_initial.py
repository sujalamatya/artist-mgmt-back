from django.db import migrations

class Migration(migrations.Migration):
    dependencies = []

    operations = [
        migrations.RunSQL(
            """
            CREATE TABLE "users" (
                id SERIAL PRIMARY KEY,
                first_name VARCHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                phone VARCHAR(15),
                dob DATE,
                gender VARCHAR(10),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                role VARCHAR(20) NOT NULL CHECK (role IN ('super_admin', 'artist_manager', 'artist'))
            );
            """
        )
    ]