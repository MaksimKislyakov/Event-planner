from rest_framework import serializers
from .models import UserProfile, Event
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'date_of_birth', 'commission', 'profile_photo', 'access_level']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'organizers', 'files', 'tasks', 'participants', 'projects']
