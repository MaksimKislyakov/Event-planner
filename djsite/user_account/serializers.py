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
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    access_level = serializers.IntegerField(required=False, default=1)
    number_phone = serializers.CharField(required=False, allow_blank=True)
    adress = serializers.CharField(required=False, allow_blank=True)
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    commission = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'username', 'password', 'full_name', 'date_of_birth', 'commission', 'profile_photo', 'access_level', 'status', 'number_phone', 'email', 'adress']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        
        # Создаем пользователя Django
        user = User.objects.create_user(
            username=username,
            password=password,
            email=validated_data.get('email', '')
        )
        
        # Создаем профиль пользователя
        profile = UserProfile.objects.create(
            user=user,
            **validated_data
        )
        
        return profile

class TasksSerializer(serializers.ModelSerializer):
    creator = serializers.HiddenField(default=serializers.CurrentUserDefault())
    executor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())
    is_past = serializers.BooleanField(required=False)

    class Meta:
        model = Tasks
        fields = ['id', 'task', 'description', 'event', 'deadline', 'creator', 'executor', 'status', 'is_past']

class EventSerializer(serializers.ModelSerializer):
    organizers = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    participants = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, required=False)
    is_past = serializers.BooleanField()
    is_cancelled = serializers.BooleanField(required=False)
    tasks = TasksSerializer(many=True, read_only=True, source='tasks_for_event')
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date', 'organizers', 'files', 'tasks', 'participants', 'projects', 'is_past', 'is_cancelled']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

