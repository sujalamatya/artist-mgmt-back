# user/views.py
from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .serializers import UserSerializer
from .jwt_utils import create_jwt_tokens, decode_jwt_token

class RegisterView(APIView):
    def post(self, request):
        # Validate incoming data using the serializer
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data

            # Hash the password before storing it in the database
            hashed_password = make_password(data['password'])

            # Insert the new user into the database using raw SQL
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    [
                        data['first_name'],
                        data['last_name'],
                        data['email'],
                        hashed_password,  # Store the hashed password
                        data.get('phone', ''),  # Optional field
                        data.get('dob', None),  # Optional field
                        data.get('gender', ''),  # Optional field
                        data.get('address', ''),  # Optional field
                        data['role'],
                    ]
                )

            # Return success response
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Return validation errors
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch the user from the database using raw SQL
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", [email])
            columns = [col[0] for col in cursor.description]
            user = cursor.fetchone()

            if user:
                user_dict = dict(zip(columns, user))

                # Verify the password
                if check_password(password, user_dict['password']):
                    # Generate access and refresh tokens
                    access_token, refresh_token = create_jwt_tokens(user_dict['id'], user_dict['role'])

                    # Return success response with tokens
                    return Response(
                        {
                            "message": "Login successful",
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "user": {
                                "id": user_dict['id'],
                                "first_name": user_dict['first_name'],
                                "last_name": user_dict['last_name'],
                                "email": user_dict['email'],
                                "role": user_dict['role'],
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    # Invalid password
                    return Response(
                        {"error": "Invalid credentials"},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                # User not found
                return Response(
                    {"error": "User not found"},
                    status=status.HTTP_404_NOT_FOUND,
                )


class ProtectedView(APIView):
    def get(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response(
                {"error": "Unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)

        if not payload:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Token is valid, return some protected data
        return Response(
            {
                "message": "You have access to this protected resource",
                "user_id": payload['user_id'],
                "role": payload['role'],
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response(
                {"error": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Decode the refresh token
        payload = decode_jwt_token(refresh_token)
        if not payload:
            return Response(
                {"error": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate a new access token
        access_token, _ = create_jwt_tokens(payload['user_id'], payload.get('role', 'user'))

        return Response(
            {
                "message": "Access token refreshed",
                "access_token": access_token,
            },
            status=status.HTTP_200_OK,
        )