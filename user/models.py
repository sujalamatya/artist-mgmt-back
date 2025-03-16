# # models.py
# from django.contrib import admin
# from django.db import models

# class User(models.Model):
#     first_name = models.CharField(max_length=255)
#     last_name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     password = models.CharField(max_length=255)
#     phone = models.CharField(max_length=20, unique=True)
#     dob = models.DateField()
#     gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
#     address = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     role = models.CharField(max_length=20, choices=[('super_admin', 'Super Admin'), ('artist_manager', 'Artist Manager'), ('artist', 'Artist')])

#     class Meta:
#         db_table = 'user'  # Ensure this matches the actual raw SQL table

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.role})"
