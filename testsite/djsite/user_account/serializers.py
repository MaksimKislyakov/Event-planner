from rest_framework import serializers
from .models import UserProfile, Event
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'date_of_birth', 'commission', 'profile_photo', 'access_level', 'status', 'number_phone', 'email', 'adress']

class EventSerializer(serializers.ModelSerializer):
    organizers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True)
    is_past = serializers.BooleanField()  
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'organizers', 'files', 'tasks', 'participants', 'projects', 'is_past']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']