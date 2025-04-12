from django.db import models

class Project(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название проекта')
    description = models.TextField(blank=True, verbose_name='Описание проекта')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    parent_project = models.ForeignKey('self', null=True, blank=False, on_delete=models.CASCADE, related_name='sub_projects', verbose_name='Родительский проект')

    def __str__(self):
        return self.title
    
class ProjectFile(models.Model):
    project = models.ForeignKey(Project, related_name='files', on_delete=models.CASCADE, verbose_name='Проект')
    file_type = models.CharField(max_length=50, verbose_name='Тип файла')
    file_url = models.URLField(verbose_name='Ссылка на файл')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    file_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.file_type} для {self.project.title}"