from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .serializers import UserProfileSerializer, EventSerializer
from .models import UserProfile, Event
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.access_level < 2: 
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)
        
        organized_events = Event.objects.filter(organizers=request.user)
        participating_events = Event.objects.filter(participants=request.user)

        event_serializer = EventSerializer(organized_events.union(participating_events), many=True)

        serializer = UserProfileSerializer(profile)
        return Response({
            'profile': serializer.data,
            'events': event_serializer.data
        })

    def put(self, request):
        try:
            profile = UserProfile.objects.get(user=request.user)
            if profile.access_level < 3:  
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class EventListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = UserProfile.objects.get(user=request.user)
        if profile.access_level < 1:  
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        events = Event.objects.all()
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = EventSerializer(data=request.data)
        if serializer.is_valid():
            event = serializer.save()

            if "organizers" in request.data:
                event.organizers.set(request.data["organizers"])

            if "participants" in request.data:
                event.participants.set(request.data["participants"])

            event.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EventDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, event_id):
        profile = UserProfile.objects.get(user=request.user)
        if profile.access_level < 1: 
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventSerializer(event)
        return Response(serializer.data)

    def put(self, request, event_id):
        profile = UserProfile.objects.get(user=request.user)
        if profile.access_level < 3:  
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = EventSerializer(event, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, event_id):
        profile = UserProfile.objects.get(user=request.user)
        if profile.access_level < 3: 
            return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(id=event_id)
            event.delete()
            return Response({"message": "Event deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({"error": "Event not found"}, status=status.HTTP_404_NOT_FOUND)

class OtherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            current_profile = UserProfile.objects.get(user=request.user)
            if current_profile.access_level < 3: 
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)