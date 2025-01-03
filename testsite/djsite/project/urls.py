from django.urls import path
from . import views

urlpatterns = [
    path('', views.project_list, name='project_list'),
    path('project/<int:pk>/', views.project_detail, name='project_detail'),
    path('project/<int:project_id>/create_google_service/', views.create_google_document, name='create_google_document'),
    path('project/create/', views.create_project, name='create_project'),
    path('project/create/<int:parent_id>/', views.create_project, name='create_project'),
]


