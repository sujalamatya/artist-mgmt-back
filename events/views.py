from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View
from django.db import connection
import json
from .serializers import EventSerializer

@method_decorator(csrf_exempt, name='dispatch')
class EventListCreateView(View):
    def get(self, request):
        """Fetch all events."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM events ORDER BY event_date DESC")
            columns = [col[0] for col in cursor.description]
            events = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return JsonResponse(events, safe=False)

    def post(self, request):
        """Create a new event."""
        try:
            data = json.loads(request.body)
            serializer = EventSerializer(data=data)

            if serializer.is_valid():
                validated_data = serializer.validated_data
                with connection.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO events (artist_id, user_id, title, description, event_date, location, created_at)
                        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, [
                        validated_data["artist_id"],
                        validated_data.get("user_id"),
                        validated_data["title"],
                        validated_data.get("description"),
                        validated_data["event_date"],
                        validated_data.get("location"),
                    ])
                    event_id = cursor.fetchone()[0]
                return JsonResponse({"message": "Event created", "id": event_id}, status=201)
            return JsonResponse({"error": serializer.errors}, status=400)
        
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@method_decorator(csrf_exempt, name='dispatch')
class EventDetailView(View):
    def get(self, request, event_id):
        """Fetch a single event by ID."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM events WHERE id = %s", [event_id])
            row = cursor.fetchone()
            if row:
                columns = [col[0] for col in cursor.description]
                event = dict(zip(columns, row))
                return JsonResponse(event)
            return JsonResponse({"error": "Event not found"}, status=404)

    def put(self, request, event_id):
        """Update an event."""
        try:
            data = json.loads(request.body)
            serializer = EventSerializer(data=data)

            if serializer.is_valid():
                validated_data = serializer.validated_data
                with connection.cursor() as cursor:
                    cursor.execute("""
                        UPDATE events 
                        SET artist_id=%s, user_id=%s, title=%s, description=%s, event_date=%s, location=%s
                        WHERE id=%s
                    """, [
                        validated_data["artist_id"],
                        validated_data.get("user_id"),
                        validated_data["title"],
                        validated_data.get("description"),
                        validated_data["event_date"],
                        validated_data.get("location"),
                        event_id,
                    ])
                return JsonResponse({"message": "Event updated"})
            return JsonResponse({"error": serializer.errors}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    def delete(self, request, event_id):
        """Delete an event."""
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM events WHERE id = %s", [event_id])
        return JsonResponse({"message": "Event deleted"})
