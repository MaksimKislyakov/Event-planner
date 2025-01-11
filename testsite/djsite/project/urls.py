from django.urls import path
from . import views

urlpatterns = [
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('projects/create/', views.CreateProjectView.as_view(), name='create_project'),
    path('projects/create/<int:parent_id>/', views.CreateProjectView.as_view(), name='create_project_with_parent'),
    path('projects/<int:project_id>/create_google_document/', views.CreateGoogleDocumentView.as_view(), name='create_google_document'),
]
