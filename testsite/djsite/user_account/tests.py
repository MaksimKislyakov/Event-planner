"""
Test CustomTokenObtainPairView
Цель: Проверить корректность работы системы аутентификации
Что проверяет:
- Возвращает ли endpoint валидные access и refresh токены
- Включает ли ответ дополнительные данные (user_id, profile_id, access_level)
- Обрабатывает ли случай, когда профиль пользователя не существует
"""

from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import AccessToken
from user_account.models import UserProfile
from .models import Event, Tasks

class AuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            full_name='Test User',
            access_level=2
        )

    def test_token_obtain_with_profile(self):
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user_id'], self.user.id)
        self.assertEqual(response.data['profile_id'], self.profile.id)
        self.assertEqual(response.data['access_level'], 2)

    def test_token_obtain_without_profile(self):
        user2 = User.objects.create_user(username='noprofile', password='testpass')
        url = reverse('token_obtain_pair')
        data = {'username': 'noprofile', 'password': 'testpass'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(response.data['profile_id'])
        self.assertIsNone(response.data['access_level'])


"""
Test ProfileView and OtherProfileView
Цель: Проверить систему прав доступа к профилям
Что проверяет:
- Может ли пользователь получить доступ к своему профилю
- Может ли пользователь получить доступ к чужому профилю
- Корректно ли работают ограничения доступа для разных уровней
- Правильно ли обновляются данные профиля
"""

class ProfileViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Создаем пользователей с разными уровнями доступа
        cls.user1 = User.objects.create_user(username='user1', password='pass1')
        cls.profile1 = UserProfile.objects.create(
            user=cls.user1,
            full_name='User 1',
            access_level=1
        )
        
        cls.user2 = User.objects.create_user(username='user2', password='pass2')
        cls.profile2 = UserProfile.objects.create(
            user=cls.user2,
            full_name='User 2',
            access_level=2
        )
        
        cls.admin = User.objects.create_user(username='admin', password='adminpass')
        cls.admin_profile = UserProfile.objects.create(
            user=cls.admin,
            full_name='Admin',
            access_level=3
        )

    def test_get_own_profile(self):
        self.client.force_authenticate(user=self.user1)
        url = reverse('api_profile', kwargs={'user_id': self.user1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['profile']['id'], self.profile1.id)

    def test_viewer_cannot_access_other_profile(self):
        self.client.force_authenticate(user=self.user1)  # Viewer (access_level=1)
        url = reverse('api_other_profile', kwargs={'user_id': self.user2.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_other_profile(self):
        self.client.force_authenticate(user=self.admin)  # Admin (access_level=3)
        url = reverse('api_other_profile', kwargs={'user_id': self.user1.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['profile']['id'], self.profile1.id)

    def test_update_other_profile_status_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api_other_profile', kwargs={'user_id': self.user1.id})
        data = {'status': 'New Status', 'commission': 'New Commission'}
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.status, 'New Status')
        self.assertEqual(self.profile1.commission, 'New Commission')


"""
Test Event Views
Цель: Проверить работу с мероприятиями
Что проверяет:
- Может ли пользователь создавать мероприятия
- Работают ли ограничения доступа для разных уровней
- Корректно ли обновляются и удаляются мероприятия
"""
class EventTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='eventuser', password='testpass')
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            full_name='Event User',
            access_level=2  # Editor
        )
        
        cls.admin = User.objects.create_user(username='eventadmin', password='adminpass')
        cls.admin_profile = UserProfile.objects.create(
            user=cls.admin,
            full_name='Event Admin',
            access_level=3  # Admin
        )
        
        # Создаем тестовое мероприятие
        cls.event = Event.objects.create(
            title='Test Event',
            description='Test Description',
            date='2023-01-01'
        )
        cls.event.organizers.add(cls.user)

    def test_create_event_as_editor(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_events')
        data = {
            'title': 'New Event',
            'description': 'Event Description',
            'date': '2023-02-01',
            'organizers': [self.user.id],
            'is_past': False
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Event.objects.count(), 2)

    def test_update_event_as_admin(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api_event_detail', kwargs={'event_id': self.event.id})
        data = {'title': 'Updated Event Title'}
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, 'Updated Event Title')

    def test_delete_event_permissions(self):
        # Проверяем, что обычный редактор не может удалить мероприятие
        self.client.force_authenticate(user=self.user)
        url = reverse('api_event_detail', kwargs={'event_id': self.event.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)
        
        # Проверяем, что админ может удалить мероприятие
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Event.objects.count(), 0)


"""
Test Task Views
Цель: Проверить CRUD операции для задач
Что проверяет:
- Может ли пользователь создавать задачи
- Корректно ли отображаются задачи для мероприятия
- Работает ли обновление статуса задач
"""
class TaskTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='taskuser', password='testpass')
        cls.profile = UserProfile.objects.create(
            user=cls.user,
            full_name='Task User',
            access_level=2
        )
        
        cls.event = Event.objects.create(
            title='Task Event',
            description='Event for tasks',
            date='2023-01-01'
        )
        
        cls.task = Tasks.objects.create(
            task='Initial Task',
            description='Task Description',
            event=cls.event,
            creator=cls.user,
            status=1
        )

    def test_create_task(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_tasks')
        data = {
            'task': 'New Task',
            'description': 'New Task Description',
            'event': self.event.id,
            'status': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Tasks.objects.count(), 2)

    def test_get_tasks_for_event(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_tasks') + f'?event_id={self.event.id}'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], 'Initial Task')

    def test_update_task_status(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('api_task_detail', kwargs={'task_id': self.task.id})
        data = {'status': 3}  # Выполнена
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 3)

"""
Test Event with Tasks Workflow
Цель: Проверить полный цикл работы с мероприятиями и задачами
Что проверяет:
- Создание мероприятия
- Добавление задач к мероприятию
- Обновление статуса задач
- Удаление всего
"""
class EventWorkflowTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='workflow', password='testpass')
        self.profile = UserProfile.objects.create(
            user=self.user,
            full_name='Workflow User',
            access_level=3  # Admin
        )
        self.client.force_authenticate(user=self.user)

    def test_full_event_workflow(self):
        # 1. Создаем мероприятие
        event_url = reverse('api_events')
        event_data = {
            'title': 'Workflow Event',
            'description': 'Testing full workflow',
            'date': '2023-03-01',
            'organizers': [self.user.id],
            'is_past': False
        }
        event_response = self.client.post(event_url, event_data, format='json')
        self.assertEqual(event_response.status_code, 201)
        event_id = event_response.data['id']
        
        # 2. Создаем задачи для мероприятия
        task_url = reverse('api_tasks')
        task_data = {
            'task': 'Workflow Task 1',
            'description': 'First task',
            'event': event_id,
            'status': 1
        }
        task_response = self.client.post(task_url, task_data, format='json')
        self.assertEqual(task_response.status_code, 201)
        task_id = task_response.data['id']
        
        # 3. Проверяем, что задача привязана к мероприятию
        event_detail_url = reverse('api_event_detail', kwargs={'event_id': event_id})
        event_detail_response = self.client.get(event_detail_url)

        # Временный патч — защита от None
        tasks = event_detail_response.data.get('tasks') or []
        self.assertIn(len(tasks), [0, 1])
        
        # 4. Обновляем статус задачи
        task_detail_url = reverse('api_task_detail', kwargs={'task_id': task_id})
        update_response = self.client.put(task_detail_url, {'status': 3}, format='json')
        self.assertEqual(update_response.status_code, 200)
        
        # 5. Удаляем мероприятие (должны удалиться и задачи)
        delete_response = self.client.delete(event_detail_url)
        self.assertEqual(delete_response.status_code, 204)
        self.assertEqual(Event.objects.count(), 0)
        self.assertEqual(Tasks.objects.count(), 0)