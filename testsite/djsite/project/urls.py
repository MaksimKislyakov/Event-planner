from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='project_list'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('create/', views.CreateProjectView.as_view(), name='create_project'),
    # path('create_parent/<int:parent_id>/', views.CreateProjectView.as_view(), name='create_project_with_parent'),
    path('<int:project_id>/create_google_service/', views.CreateGoogleDocumentView.as_view(), name='create_google_service'),
]
