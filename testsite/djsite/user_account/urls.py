from django.urls import path
from . import views

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('event/<int:event_id>/', views.event_detail, name='event_detail'),

    path('event/create/', views.create_event, name='create_event'),
    
    path('event/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('event/<int:event_id>/manage_participants/', views.manage_participants, name='manage_participants'),
    path('event/<int:event_id>/delete/', views.delete_event, name='delete_event'),
    path('events/<str:date>/', views.events_by_date_view, name='events_by_date'),
    path('event/<int:event_id>/manage_projects/', views.manage_event_projects, name='manage_event_projects'),
    # path('create_event/<str:date>/', views.create_event_view, name='create_event'),
]
