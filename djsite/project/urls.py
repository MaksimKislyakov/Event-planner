from django.urls import path
from . import views
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
          openapi.Info(
              title="My API",
              default_version='v1',
              description="Описание моего API",
              terms_of_service="https://example.com/terms/",
              contact=openapi.Contact(email="contact@example.com"),
              license=openapi.License(name="BSD License"),
          ),
          public=True,
          permission_classes=[permissions.AllowAny],
      )


urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.CreateProjectView.as_view(), name='create_project'),
    # path('create_parent/<int:parent_id>/', views.CreateProjectView.as_view(), name='create_project_with_parent'),
    path('<int:project_id>/create_google_service/', views.CreateGoogleDocumentView.as_view(), name='create_google_service'),
    path('project_file/<int:file_id>/', views.CreateGoogleDocumentView.as_view(), name='delete_project_file'),
]
