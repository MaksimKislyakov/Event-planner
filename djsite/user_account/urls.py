from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/users/', views.UserListView.as_view(), name='api_user_list'),
    path('api/profile/<int:user_id>/', views.ProfileView.as_view(), name='api_profile'),
    path('api/profile_view/<int:user_id>/', views.OtherProfileView.as_view(), name='api_other_profile'),
    path('api/events/', views.EventListCreateView.as_view(), name='api_events'),
    path('api/event/<int:event_id>/', views.EventDetailView.as_view(), name='api_event_detail'),
    path('api/tasks/', views.TaskListCreateView.as_view(), name='api_tasks'),
    path('api/tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='api_task_detail'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name ='token_refresh'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)