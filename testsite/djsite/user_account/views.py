from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, EventParticipantsForm
from .models import Event
from django.forms import ModelForm
from django.http import HttpResponseForbidden, HttpResponse, HttpResponseBadRequest
from datetime import datetime, date, timedelta
from .utils import get_month_dates, get_week_dates, get_day_date
import calendar


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

def calendar_view(request):
    view_type = request.GET.get('view', 'month')
    today = date.today()

    # Получаем год, месяц и день из GET-запроса
    try:
        year = int(request.GET.get('year', today.year))
        month = int(request.GET.get('month', today.month))
        day = int(request.GET.get('day', today.day))
    except ValueError:
        return HttpResponseBadRequest("Invalid date input.")

    context = {
        'view': view_type,
        'year': year,
        'month': month,
        'day': day,
    }

    if view_type == 'month':
        # Генерация сетки для месяца
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.itermonthdates(year, month)
        weeks = []
        week = []

        for single_date in month_days:
            if len(week) == 7:  # Каждая неделя состоит из 7 дней
                weeks.append(week)
                week = []
            week.append(single_date)

        if week:
            weeks.append(week)

        # Получаем события за текущий месяц
        events = Event.objects.filter(date__year=year, date__month=month)
        event_dict = {event.date: event for event in events}

        context['dates'] = weeks
        context['events'] = event_dict  # Словарь {дата: событие}

    elif view_type == 'week':
        selected_date = date(year, month, day)
        start_of_week = selected_date - timedelta(days=selected_date.weekday())
        dates = [start_of_week + timedelta(days=i) for i in range(7)]

        events = Event.objects.filter(date__range=(dates[0], dates[-1]))
        event_dict = {event.date: event for event in events}

        context['dates'] = dates
        context['events'] = event_dict

    elif view_type == 'day':
        selected_date = date(year, month, day)
        events = Event.objects.filter(date=selected_date)

        context['dates'] = [selected_date]
        context['events'] = {selected_date: events}

    else:
        return HttpResponseBadRequest("Invalid view type.")

    return render(request, f'calendar/{view_type}_view.html', context)