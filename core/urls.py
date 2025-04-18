from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.http import HttpResponse
from .views import (
    CourseViewSet, ModuleViewSet, LessonViewSet, AssignmentViewSet, SubmissionViewSet,
    EnrollmentViewSet, LessonProgressViewSet, CertificateViewSet, MessageViewSet
)

router = DefaultRouter()

router.register(r'courses', CourseViewSet, basename='course')
router.register(r'modules', ModuleViewSet, basename='module')
router.register(r'lessons', LessonViewSet, basename='lesson')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'enrollments', EnrollmentViewSet, basename='enrollment')
router.register(r'lesson-progress', LessonProgressViewSet, basename='lesson-progress')
router.register(r'certificates', CertificateViewSet, basename='certificate')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    # Health check endpoint
    path('health/', lambda request: HttpResponse('OK'), name='health-check'),
]
