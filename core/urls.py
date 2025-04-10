from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet, ModuleViewSet, LessonViewSet, AssignmentViewSet, SubmissionViewSet,
    EnrollmentViewSet, LessonProgressViewSet, CertificateViewSet, MessageViewSet
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'lessons', LessonViewSet)
router.register(r'assignments', AssignmentViewSet)
router.register(r'submissions', SubmissionViewSet)
router.register(r'enrollments', EnrollmentViewSet)
router.register(r'lesson-progress', LessonProgressViewSet)
router.register(r'certificates', CertificateViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
