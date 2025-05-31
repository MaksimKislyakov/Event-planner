from django.contrib.auth.models import User
from django.db import models
from project.models import Project
from datetime import date
from phonenumber_field.modelfields import PhoneNumberField

class UserProfile(models.Model):
    """
    Модель профиля пользователя, расширяющая стандартную модель User Django.
    
    Attributes:
        user (OneToOneField): Связь один-к-одному с моделью User Django
        full_name (CharField): Полное имя пользователя
        date_of_birth (DateField): Дата рождения (опционально)
        commission (CharField): Комиссия или отдел пользователя
        status (CharField): Статус пользователя
        number_phone (PhoneNumberField): Номер телефона в российском формате
        email (EmailField): Email адрес
        adress (CharField): Адрес пользователя
        profile_photo (ImageField): Фотография профиля
        access_level (PositiveSmallIntegerField): Уровень доступа пользователя (1-Viewer, 2-Editor, 3-Admin)
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    commission = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=150, blank=True)
    number_phone = PhoneNumberField(blank=True, region='RU')
    email = models.EmailField(blank=True)
    adress = models.CharField(blank=True, max_length=200)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True)

    ACCESS_LEVELS = [
        (1, 'Viewer'),
        (2, 'Editor'),
        (3, 'Admin'),
    ]
    access_level = models.PositiveSmallIntegerField(choices=ACCESS_LEVELS, default=1)

    def __str__(self):
        return self.user.username


class Event(models.Model):
    """
    Модель мероприятия или события.
    
    Attributes:
        title (CharField): Название мероприятия
        description (TextField): Описание мероприятия
        date (DateField): Дата проведения
        organizers (ManyToManyField): Связь с пользователями-организаторами
        files (FileField): Прикрепленные файлы
        participants (ManyToManyField): Связь с участниками мероприятия
        projects (ManyToManyField): Связь с проектами, связанными с мероприятием
        is_past (IntegerField): Флаг, указывающий, что мероприятие в прошлом
        is_cancelled (BooleanField): Флаг отмены мероприятия
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date = models.DateField()
    organizers = models.ManyToManyField(User, related_name='organized_events', blank=True)
    files = models.FileField(upload_to='event_files/', blank=True, null=True)
    participants = models.ManyToManyField(User, related_name='events', blank=True)
    projects = models.ManyToManyField(Project, related_name='events', blank=True)
    is_past = models.IntegerField(default=0)
    is_cancelled = models.BooleanField(null=True, blank=True, default=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # После сохранения обновляем is_past у всех задач этого мероприятия
        from .models import Tasks
        is_event_past = self.is_past or self.is_cancelled
        Tasks.objects.filter(event=self).update(is_past=is_event_past)

    def __str__(self):
        return self.title

class Tasks(models.Model):
    """
    Модель задачи, связанной с мероприятием.
    
    Attributes:
        task (CharField): Название задачи
        description (CharField): Описание задачи
        event (ForeignKey): Связь с мероприятием
        deadline (DateField): Срок выполнения
        creator (ForeignKey): Создатель задачи
        executor (ManyToManyField): Исполнители задачи
        status (PositiveSmallIntegerField): Статус задачи (1-В процессе, 2-Не начата, 3-Выполнена)
        is_past (BooleanField): Флаг, указывающий, что задача в прошлом
    """
    task = models.CharField(max_length=20000)
    description = models.CharField(blank=True, max_length=20000)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='tasks_for_event')
    deadline = models.DateField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    executor = models.ManyToManyField(User, related_name='executed_tasks', blank=True)
    STATUS = [
        (1, 'В процессе'),
        (2, 'Не начата'),
        (3, 'Выполнена')
    ]
    status = models.PositiveSmallIntegerField(choices=STATUS, default=2)
    is_past = models.BooleanField(default=False)
    
    def __str__(self):
        return self.task
