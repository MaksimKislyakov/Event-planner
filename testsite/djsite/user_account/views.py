from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import UserProfileForm, EventParticipantsForm, EventForm
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
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.itermonthdates(year, month)
        weeks = []
        week = []

        for single_date in month_days:
            if len(week) == 7: 
                weeks.append(week)
                week = []
            week.append(single_date)

        if week:
            weeks.append(week)

        # Получаем события за текущий месяц
        events = Event.objects.filter(date__year=year, date__month=month)
        events_by_date = {}

        for event in events:
            if event.date not in events_by_date:
                events_by_date[event.date] = []
            events_by_date[event.date].append(event)

        context['dates'] = weeks
        context['events_by_date'] = events_by_date  # Словарь {дата: [события]}

    return render(request, 'calendar/month_view.html', context)


def events_by_date_view(request, date):
    try:
        # Преобразуем дату из строки в объект даты
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date input.")

    # Получаем события для этой даты
    events = Event.objects.filter(date=selected_date)

    # Обрабатываем POST-запрос для создания нового события
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            # Сохраняем новое событие с выбранной датой
            new_event = form.save(commit=False)
            new_event.date = selected_date
            new_event.save()
            # Перенаправляем обратно на эту же страницу
            return redirect('events_by_date', date=date)
    else:
        form = EventForm()

    # Контекст для передачи в шаблон
    context = {
        'date': selected_date,
        'events': events,
        'form': form,
    }
    return render(request, 'calendar/events_by_date.html', context)