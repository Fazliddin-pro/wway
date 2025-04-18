from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)

User = get_user_model()

class CoreTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='adminpass',
            role='admin'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='studentpass',
            role='student'
        )
        self.client = APIClient()

    def test_course_creation(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('course-list')
        data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'category': 'Programming',
            'level': 'beginner'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.get().title, 'Test Course')

    def test_module_creation(self):
        self.client.force_authenticate(user=self.admin)
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='beginner',
            teacher=self.admin
        )
        url = reverse('module-list')
        data = {
            'title': 'Test Module',
            'description': 'Test Description',
            'course': course.id,
            'order': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Module.objects.count(), 1)
        self.assertEqual(Module.objects.get().title, 'Test Module')

    def test_lesson_creation(self):
        self.client.force_authenticate(user=self.admin)
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='beginner',
            teacher=self.admin
        )
        module = Module.objects.create(
            title='Test Module',
            description='Test Description',
            course=course,
            order=1
        )
        url = reverse('lesson-list')
        data = {
            'title': 'Test Lesson',
            'content': 'Test Content',
            'module': module.id,
            'order': 1,
            'lesson_type': 'text'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 1)
        self.assertEqual(Lesson.objects.get().title, 'Test Lesson')

    def test_enrollment(self):
        self.client.force_authenticate(user=self.student)
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='beginner',
            teacher=self.admin
        )
        url = reverse('enrollment-list')
        data = {
            'course': course.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Enrollment.objects.count(), 1)
        self.assertEqual(Enrollment.objects.get().user, self.student)

    def test_lesson_progress(self):
        self.client.force_authenticate(user=self.student)
        course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='beginner',
            teacher=self.admin
        )
        module = Module.objects.create(
            title='Test Module',
            description='Test Description',
            course=course,
            order=1
        )
        lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Test Content',
            module=module,
            order=1,
            lesson_type='text'
        )
        url = reverse('lesson-progress-list')
        data = {
            'lesson': lesson.id,
            'status': 'completed',
            'time_spent': 30
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(LessonProgress.objects.count(), 1)
        self.assertEqual(LessonProgress.objects.get().status, 'completed')

    def test_message_creation(self):
        self.client.force_authenticate(user=self.student)
        url = reverse('message-list')
        data = {
            'receiver': self.admin.id,
            'content': 'Test Message'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        self.assertEqual(Message.objects.get().content, 'Test Message')
