from django.urls import path
from . import views

urlpatterns = [
    path('api/profile/', views.ProfileView.as_view(), name='api_profile'),
    path('api/events/', views.EventListCreateView.as_view(), name='api_events'),
    path('api/event/<int:event_id>/', views.EventDetailView.as_view(), name='api_event_detail'),
]