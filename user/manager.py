# from django.db import connection
# from django.contrib.auth.hashers import make_password, check_password
# from django.utils.translation import gettext_lazy as _
# from .constants import UserRole  # Import roles

# class CustomUserManager:
#     @staticmethod
#     def create_user(email, password, **extra_fields):
#         if not email:
#             raise ValueError(_("The Email must be set"))

#         role = extra_fields.get("role", "artist")  # Default role is 'artist'
#         if role not in UserRole.CHOICES:
#             raise ValueError(_("Invalid role provided"))

#         hashed_password = make_password(password)

#         with connection.cursor() as cursor:
#             cursor.execute("""
#                 INSERT INTO "user" (email, password, first_name, last_name, phone, dob, gender, address, role, created_at, updated_at) 
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
#                 RETURNING id;
#             """, [
#                 email, hashed_password, extra_fields.get("first_name", ""), extra_fields.get("last_name", ""),
#                 extra_fields.get("phone", ""), extra_fields.get("dob", ""), extra_fields.get("gender", ""),
#                 extra_fields.get("address", ""), role
#             ])
#             user_id = cursor.fetchone()

#         if not user_id:
#             raise ValueError(_("User creation failed"))

#         return {"id": user_id[0], "email": email, "role": role}

#     @staticmethod
#     def create_superuser(email, password, **extra_fields):
#         extra_fields.setdefault("role", UserRole.SUPER_ADMIN)  # Force role as super_admin
#         return CustomUserManager.create_user(email, password, **extra_fields)

#     @staticmethod
#     def authenticate(email, password):
#         with connection.cursor() as cursor:
#             cursor.execute("""SELECT id, password, role FROM "user" WHERE email = %s""", [email])
#             user = cursor.fetchone()

#             if user and check_password(password, user[1]):
#                 return {"id": user[0], "email": email, "role": user[2]}  # Return user details

#         raise ValueError(_("Invalid credentials provided"))
