from django import forms
from .models import UserProfile, Event, User
from project.models import Project


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'date_of_birth', 'commission', 'profile_photo', 'access_level']

class EventParticipantsForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['participants']
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Название события'}),
            'description': forms.Textarea(attrs={'placeholder': 'Описание события'}),
        }

class EventProjectForm(forms.ModelForm):
    projects = forms.ModelMultipleChoiceField(
        queryset=Project.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Event
        fields = ['projects']