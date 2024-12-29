from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, EventParticipantsForm
from .models import Event
from django.forms import ModelForm
from django.http import HttpResponseForbidden


@login_required
def profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    events = request.user.events.all() 
    return render(request, 'account/profile.html', {'profile': profile, 'events': events})

@login_required
def edit_profile(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'account/edit_profile.html', {'form': form})

@login_required
def calendar_view(request):
    events = Event.objects.all()
    return render(request, 'calendar/calendar.html', {'events': events})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'calendar/event_detail.html', {'event': event})

def check_access_level(min_level):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user_profile = UserProfile.objects.get(user=request.user)
            if user_profile.access_level < min_level:
                return HttpResponseForbidden("У вас недостаточно прав для выполнения этого действия.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class EventForm(ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'tasks', 'files']

@login_required
@check_access_level(2)
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save()
            return redirect('calendar')
    else:
        form = EventForm()
    return render(request, 'calendar/create_event.html', {'form': form})

@login_required
@check_access_level(2)
def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventForm(instance=event)
    return render(request, 'calendar/edit_event.html', {'form': form})

from django.shortcuts import get_object_or_404

@login_required
@check_access_level(2)
def manage_participants(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == 'POST':
        form = EventParticipantsForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('event_detail', event_id=event.id)
    else:
        form = EventParticipantsForm(instance=event)
    return render(request, 'calendar/manage_participants.html', {'form': form, 'event': event})

@login_required
@check_access_level(3)
def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect('calendar')

