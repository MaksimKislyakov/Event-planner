from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('api/profile/', views.ProfileView.as_view(), name='api_profile'),
    path('api/events/', views.EventListCreateView.as_view(), name='api_events'),
    path('api/event/<int:event_id>/', views.EventDetailView.as_view(), name='api_event_detail'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name ='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh')
]