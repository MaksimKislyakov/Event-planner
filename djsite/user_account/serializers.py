from rest_framework import serializers
from .models import UserProfile, Event, Tasks
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    status = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
        help_text="Должность пользователя"
    )
    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'full_name', 'date_of_birth', 'commission', 'profile_photo', 'access_level', 'status', 'number_phone', 'email', 'adress']

class EventSerializer(serializers.ModelSerializer):
    organizers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    is_past = serializers.BooleanField()  
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'organizers', 'files', 'tasks', 'participants', 'projects', 'is_past']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class TasksSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    executor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Tasks
        fields = ['id', 'task', 'description', 'event', 'deadline', 'creator', 'executor', 'status']

