from django.contrib import admin
from .models import Project, ProjectFile

class ProjectFileInline(admin.TabularInline):
    model = ProjectFile
    extra = 1

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'parent_project')
    inlines = [ProjectFileInline]

@admin.register(ProjectFile)
class ProjectFileAdmin(admin.ModelAdmin):
    list_display = ('project', 'file_type', 'file_url', 'created_at')