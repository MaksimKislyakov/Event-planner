from django import forms
from .models import UserProfile, Event, User


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