from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password, check_password
from .serializers import UserSerializer
from .jwt_utils import create_jwt_tokens, decode_jwt_token

class UserManagementView(APIView):

    def check_auth(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authentication credentials were not provided."}, 
                         status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        
        if isinstance(payload, dict) and "error" in payload:
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
            
        if payload.get('role') != 'super_admin':
            return Response({"error": "Forbidden - Admin access required"}, 
                         status=status.HTTP_403_FORBIDDEN)
        return payload

    def get(self, request):
        auth = self.check_auth(request)
        if isinstance(auth, Response):
            return auth

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, first_name, last_name, email, phone, dob, gender, address, role FROM users")
            columns = [col[0] for col in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response(users, status=status.HTTP_200_OK)

    def post(self, request):
        # Check permissions
        error_response = self.check_super_admin(request)
        if error_response:
            return error_response

        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            hashed_password = make_password(data['password'])

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password, phone, dob, gender, address, role)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, first_name, last_name, email, phone, dob, gender, address, role
                    """,
                    [
                        data['first_name'],
                        data['last_name'],
                        data['email'],
                        hashed_password,
                        data.get('phone', ''),
                        data.get('dob', None),
                        data.get('gender', ''),
                        data.get('address', ''),
                        data['role'],
                    ]
                )
                columns = [col[0] for col in cursor.description]
                user = dict(zip(columns, cursor.fetchone()))

            return Response(user, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    def check_auth(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authentication credentials were not provided."}, 
                         status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)
        
        if isinstance(payload, dict) and "error" in payload:
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)
            
        if payload.get('role') != 'super_admin':
            return Response({"error": "Forbidden - Admin access required"}, 
                         status=status.HTTP_403_FORBIDDEN)
        
        return payload

    def get(self, request, user_id):
        auth_result = self.check_auth(request)
        if isinstance(auth_result, Response):
            return auth_result
            
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, first_name, last_name, email, phone, dob, gender, address, role FROM users WHERE id = %s",
                [user_id]
            )
            columns = [col[0] for col in cursor.description]
            user = cursor.fetchone()

            if not user:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

            user_dict = dict(zip(columns, user))

        return Response(user_dict, status=status.HTTP_200_OK)

    def put(self, request, user_id):
        auth_result = self.check_auth(request)
        if isinstance(auth_result, Response):
            return auth_result

        serializer = UserSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        update_fields = []
        update_values = []

        if 'password' in data:
            data['password'] = make_password(data['password'])
        
        for field, value in data.items():
            update_fields.append(f"{field} = %s")
            update_values.append(value)

        if not update_fields:
            return Response({"error": "No fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        update_values.append(user_id)
        
        with connection.cursor() as cursor:
            query = f"""
                UPDATE users 
                SET {', '.join(update_fields)} 
                WHERE id = %s
                RETURNING id, first_name, last_name, email, phone, dob, gender, address, role
            """
            cursor.execute(query, update_values)
            columns = [col[0] for col in cursor.description]
            updated_user = dict(zip(columns, cursor.fetchone()))

        return Response(updated_user, status=status.HTTP_200_OK)

    def delete(self, request, user_id):
        auth_result = self.check_auth(request)  # Changed from check_super_admin to check_auth
        if isinstance(auth_result, Response):
            return auth_result

        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s RETURNING id", [user_id])
            if cursor.rowcount == 0:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "User deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            hashed_password = make_password(data['password'])

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
                        hashed_password,
                        data.get('phone', ''),
                        data.get('dob', None),
                        data.get('gender', ''),
                        data.get('address', ''),
                        data['role'],
                    ]
                )

            return Response({"message": "User registered successfully","status":status.HTTP_201_CREATED}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", [email])
            columns = [col[0] for col in cursor.description]
            user = cursor.fetchone()

            if user:
                user_dict = dict(zip(columns, user))

                if check_password(password, user_dict['password']):
                    access_token, refresh_token = create_jwt_tokens(user_dict['id'], user_dict['role'])

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
                                "phone": user_dict['phone'],
                                "gender": user_dict['gender'],
                                "dob": user_dict['dob'],
                                "address": user_dict['address'],
                                "role": user_dict['role'],
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)


class ProtectedView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(' ')[1]
        payload = decode_jwt_token(token)

        if isinstance(payload, dict) and "error" in payload:
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "message": "You have access to this protected resource",
                "user_id": payload['id'],  # Changed from 'user_id' to 'id'
                "role": payload['role'],
            },
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')

        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=status.HTTP_400_BAD_REQUEST)

        payload = decode_jwt_token(refresh_token)

        if isinstance(payload, dict) and "error" in payload:
            return Response(payload, status=status.HTTP_401_UNAUTHORIZED)

        access_token, _ = create_jwt_tokens(payload['id'], payload.get('role', 'user'))

        return Response(
            {
                "message": "Access token refreshed",
                "access_token": access_token,
            },
            status=status.HTTP_200_OK,
        )
