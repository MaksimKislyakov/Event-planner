import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.decorators import api_view
from .serializers import UserProfileSerializer, EventSerializer, TasksSerializer
from .models import UserProfile, Event, Tasks
# from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
# from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        try:
            profile = UserProfile.objects.get(user=self.user)
            data['user_id'] = self.user.id
            data['profile_id'] = profile.id
            data['access_level'] = profile.access_level
        except UserProfile.DoesNotExist:
            data['user_id'] = self.user.id
            data['profile_id'] = None
            data['access_level'] = None

        return data

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
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

    def put(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        profile_photo_path = request.data.get('profile_photos', None)

        if profile_photo_path:
            file_path = os.path.join(settings.MEDIA_ROOT, profile_photo_path.lstrip('/'))

            if os.path.exists(file_path):
                profile.profile_photo = profile_photo_path
            else:
                return Response({"error": "File not found"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OtherProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        try:
            current_profile = UserProfile.objects.get(user=request.user)
            if current_profile.access_level < 3:
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        user = profile.user
        organized_events = Event.objects.filter(organizers=user)
        participating_events = Event.objects.filter(participants=user)

        event_serializer = EventSerializer(organized_events.union(participating_events), many=True)

        profile_serializer = UserProfileSerializer(profile)

        return Response({
            'profile': profile_serializer.data,
            'events': event_serializer.data
        })
    
    def put(self, request, user_id):
        try:
            current_profile = UserProfile.objects.get(user=request.user)
            if current_profile.access_level  < 3:
                return Response({"error": "Access denied"}, status=status.HTTP_403_FORBIDDEN)

            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

        if 'commission' not in request.data:
            return Response({"error": "Only commission field can be updated"}, status=status.HTTP_400_BAD_REQUEST)
        
        if 'status' not in request.data:
            return Response({"error": "Only status field can be updated"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserProfileSerializer(profile, data={'commission': request.data['commission'], 'status': request.data['status']}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            users = UserProfile.objects.all()
            serializer = UserProfileSerializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        

class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        event_id = request.query_params.get('event_id')
        if event_id:
            tasks = Tasks.objects.filter(event_id=event_id)
        else:
            tasks = Tasks.objects.all()
        
        serializer = TasksSerializer(tasks, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TasksSerializer(
            data=request.data,
            context={'request': request}  
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, task_id):
        return get_object_or_404(Tasks, id=task_id)

    def get(self, request, task_id):
        task = self.get_object(task_id)
        serializer = TasksSerializer(task)
        return Response(serializer.data)

    def put(self, request, task_id):
        task = self.get_object(task_id)
        serializer = TasksSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, task_id):
        task = self.get_object(task_id)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)