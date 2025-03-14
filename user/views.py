from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .manager import CustomUserManager
from .constants import UserRole  # Import roles

class RegisterView(APIView):
    def post(self, request):
        """User Registration"""
        data = request.data
        try:
            user = CustomUserManager.create_user(
                email=data["email"],
                password=data["password"],
                first_name=data.get("first_name", ""),
                last_name=data.get("last_name", ""),
                phone=data.get("phone", ""),
                dob=data.get("dob", ""),
                gender=data.get("gender", ""),
                address=data.get("address", ""),
                role=data.get("role", UserRole.ARTIST),  # Default role: artist
            )
            return Response({"message": "User registered successfully", "user": user}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        """User Login"""
        data = request.data
        user = CustomUserManager.authenticate(email=data["email"], password=data["password"])
        
        if user:
            return Response({"message": "Login successful", "user": user}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
