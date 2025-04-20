from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer,
    AssignmentSerializer, SubmissionSerializer, EnrollmentSerializer,
    LessonProgressSerializer, CertificateSerializer, MessageSerializer
)
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock

User = get_user_model()

class CoreTests(APITestCase):
    def setUp(self):
        Course.objects.all().delete()
        Module.objects.all().delete()
        Lesson.objects.all().delete()
        Assignment.objects.all().delete()
        Certificate.objects.all().delete()
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='admin123',
            phone_number='+998901234567',
            role='admin'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='teacher123',
            phone_number='+998901234568',
            role='teacher'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='student123',
            phone_number='+998901234569',
            role='student'
        )

        self.course_data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'category': 'Programming',
            'level': 'Beginner',
            'accessibility_features': ['subtitles']
        }

        self.course = Course.objects.create(
            teacher=self.teacher,
            **self.course_data
        )

        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Module Description',
            order=1
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Test Lesson',
            content='Test Content',
            order=1
        )

        self.assignment = Assignment.objects.create(
            lesson=self.lesson,
            title='Test Assignment',
            description='Test Assignment Description',
            due_date=timezone.now() + timezone.timedelta(days=7)
        )

    def test_course_creation(self):
        """Test course creation"""
        url = reverse('course-list')
        data = {
            'title': 'New Test Course',
            'description': 'Test Description',
            'category': 'Programming',
            'level': 'beginner',
            'is_active': True
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Course.objects.count(), 2)

    def test_module_creation(self):
        Course.objects.all().delete()
        Module.objects.all().delete()
        
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
        Course.objects.all().delete()
        Module.objects.all().delete()
        Lesson.objects.all().delete()
        
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

    def test_course_serializer(self):
        data = {
            'title': 'Test Course',
            'description': 'Test Description',
            'category': 'Programming',
            'level': 'Beginner',
            'accessibility_features': 'subtitles',
            'is_active': True
        }
        request = type('Request', (), {'user': self.teacher})()
        serializer = CourseSerializer(data=data, context={'request': request})
        if not serializer.is_valid():
            print("Course serializer errors:", serializer.errors)
        self.assertTrue(serializer.is_valid())

    def test_certificate_serializer(self):
        data = {
            'course': self.course.id,
            'certificate_number': 'TEST-001'
        }
        request = type('Request', (), {'user': self.student})()
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.course.is_active = False
        self.course.save()
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        
        self.course.is_active = True
        self.course.save()
        Certificate.objects.create(
            course=self.course,
            user=self.student,
            certificate_number='TEST-001'
        )
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_submission_serializer(self):
        data = {
            'assignment': self.assignment.id,
            'submitted_file': SimpleUploadedFile("file.txt", b"file_content")
        }
        serializer = SubmissionSerializer(data=data, context={'request': Mock(user=self.student)})
        self.assertTrue(serializer.is_valid())

class SerializerTests(APITestCase):
    def setUp(self):
        Course.objects.all().delete()
        Module.objects.all().delete()
        Lesson.objects.all().delete()
        Assignment.objects.all().delete()
        Certificate.objects.all().delete()
        
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            role='admin',
            phone_number='+998901234567'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='testpass123',
            role='teacher',
            phone_number='+998901234568'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='testpass123',
            role='student',
            phone_number='+998901234569'
        )
        
        self.course = Course.objects.create(
            title='Test Course',
            description='Test Description',
            teacher=self.teacher,
            is_active=True,
            category='Programming',
            level='Beginner'
        )
        
        self.module = Module.objects.create(
            title='Test Module',
            description='Test Description',
            course=self.course,
            order=1,
            is_active=True
        )
        
        self.lesson = Lesson.objects.create(
            title='Test Lesson',
            content='Test Content',
            module=self.module,
            order=1,
            is_active=True
        )
        
        self.assignment = Assignment.objects.create(
            title='Test Assignment',
            description='Test Description',
            lesson=self.lesson,
            is_active=True
        )

    def test_course_serializer(self):
        data = {
            'title': 'New Course',
            'description': 'New Description',
            'category': 'Programming',
            'level': 'Beginner'
        }
        request = type('Request', (), {'user': self.teacher})()
        serializer = CourseSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        request.user = self.student
        serializer = CourseSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_module_serializer(self):
        data = {
            'title': 'New Module',
            'description': 'New Description',
            'course': self.course.id,
            'order': 2
        }
        request = type('Request', (), {'user': self.teacher})()
        serializer = ModuleSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.course.is_active = False
        self.course.save()
        serializer = ModuleSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_lesson_serializer(self):
        data = {
            'title': 'New Lesson',
            'content': 'New Content',
            'module': self.module.id,
            'order': 2
        }
        request = type('Request', (), {'user': self.teacher})()
        serializer = LessonSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        data['order'] = 1
        serializer = LessonSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)

    def test_assignment_serializer(self):
        data = {
            'title': 'New Assignment',
            'description': 'New Description',
            'lesson': self.lesson.id
        }
        request = type('Request', (), {'user': self.teacher})()
        serializer = AssignmentSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.lesson.is_active = False
        self.lesson.save()
        serializer = AssignmentSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_submission_serializer(self):
        data = {
            'assignment': self.assignment.id,
            'submitted_file': SimpleUploadedFile("file.txt", b"file_content")
        }
        request = type('Request', (), {'user': self.student})()
        serializer = SubmissionSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.assignment.is_active = False
        self.assignment.save()
        serializer = SubmissionSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_enrollment_serializer(self):
        data = {
            'course': self.course.id
        }
        request = type('Request', (), {'user': self.student})()
        serializer = EnrollmentSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.course.is_active = False
        self.course.save()
        serializer = EnrollmentSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_lesson_progress_serializer(self):
        data = {
            'lesson': self.lesson.id,
            'status': 'completed',
            'time_spent': 30
        }
        request = type('Request', (), {'user': self.student})()
        serializer = LessonProgressSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.lesson.is_active = False
        self.lesson.save()
        serializer = LessonProgressSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_certificate_serializer(self):
        data = {
            'course': self.course.id,
            'certificate_number': 'TEST-001'
        }
        request = type('Request', (), {'user': self.student})()
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        
        self.course.is_active = False
        self.course.save()
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())
        
        self.course.is_active = True
        self.course.save()
        Certificate.objects.create(
            course=self.course,
            user=self.student,
            certificate_number='TEST-001'
        )
        serializer = CertificateSerializer(data=data, context={'request': request})
        self.assertFalse(serializer.is_valid())

    def test_message_serializer(self):
        data = {
            'receiver': self.teacher.id,
            'content': 'Test Message'
        }
        request = type('Request', (), {'user': self.student})()
        serializer = MessageSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())

class APITests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='admin123',
            phone_number='+998901234567',
            role='admin'
        )
        self.teacher = User.objects.create_user(
            email='teacher@example.com',
            password='teacher123',
            phone_number='+998901234568',
            role='teacher'
        )
        self.student = User.objects.create_user(
            email='student@example.com',
            password='student123',
            phone_number='+998901234569',
            role='student'
        )

        self.course = Course.objects.create(
            teacher=self.teacher,
            title='Test Course',
            description='Test Description',
            category='Programming',
            level='Beginner',
            is_active=True
        )

        self.module = Module.objects.create(
            course=self.course,
            title='Test Module',
            description='Test Description',
            order=1,
            is_active=True
        )

        self.lesson = Lesson.objects.create(
            module=self.module,
            title='Test Lesson',
            content='Test Content',
            order=1,
            is_active=True
        )

        self.assignment = Assignment.objects.create(
            lesson=self.lesson,
            title='Test Assignment',
            description='Test Description',
            is_active=True
        )

    def test_course_api(self):
        self.client.force_authenticate(user=self.teacher)
        data = {
            'title': 'API Test Course',
            'description': 'API Test Description',
            'category': 'Programming',
            'level': 'Beginner',
            'accessibility_features': 'subtitles',
            'is_active': True
        }
        response = self.client.post('/api/v1/core/courses/', data, format='json')
        print("Course API response:", response.data)
        self.assertEqual(response.status_code, 201)

    def test_module_api(self):
        """Test module API"""
        url = reverse('module-list')
        data = {
            'course': self.course.id,
            'title': 'Test Module',
            'description': 'Test Description',
            'order': 2,
            'is_active': True
        }
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Module.objects.count(), 2)

    def test_lesson_api(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/v1/core/lessons/', {
            'title': 'New Lesson',
            'content': 'New Content',
            'module': self.module.id,
            'order': 2
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/v1/core/lessons/', {
            'title': 'New Lesson',
            'content': 'New Content',
            'module': self.module.id,
            'order': 3
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_assignment_api(self):
        self.client.force_authenticate(user=self.teacher)
        response = self.client.post('/api/v1/core/assignments/', {
            'title': 'New Assignment',
            'description': 'New Description',
            'lesson': self.lesson.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/v1/core/assignments/', {
            'title': 'New Assignment',
            'description': 'New Description',
            'lesson': self.lesson.id
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_submission_api(self):
        """Test submission API"""
        url = reverse('submission-list')
        data = {
            'assignment': self.assignment.id,
            'submitted_file': SimpleUploadedFile("test.txt", b"test content")
        }
        self.client.force_authenticate(user=self.student)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Submission.objects.count(), 1)

    def test_enrollment_api(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/v1/core/enrollments/', {
            'course': self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post('/api/v1/core/enrollments/', {
            'course': self.course.id
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_lesson_progress_api(self):
        self.client.force_authenticate(user=self.student)
        data = {
            'lesson': self.lesson.id,
            'status': 'completed'
        }
        response = self.client.post('/api/v1/core/lesson-progress/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_certificate_api(self):
        """Test certificate API"""
        url = reverse('certificate-list')
        data = {
            'course': self.course.id,
            'certificate_number': 'TEST-002'
        }
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Certificate.objects.count(), 1)

    def test_message_api(self):
        self.client.force_authenticate(user=self.student)
        response = self.client.post('/api/v1/core/messages/', {
            'receiver': self.teacher.id,
            'content': 'Test Message'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post('/api/v1/core/messages/', {
            'receiver': self.student.id,
            'content': 'Test Message'
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
