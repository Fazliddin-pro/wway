from rest_framework import viewsets, permissions, filters
from rest_framework.pagination import PageNumberPagination
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
import logging
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)
from .serializers import (
    CourseSerializer, ModuleSerializer, LessonSerializer,
    AssignmentSerializer, SubmissionSerializer, EnrollmentSerializer,
    LessonProgressSerializer, CertificateSerializer, MessageSerializer
)

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsAdminOrTeacherOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.role in ['admin', 'teacher'])

class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'student')

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related('teacher').all()
    serializer_class = CourseSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['category', 'level']
    search_fields = ['title', 'description', 'category']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        try:
            if Course.objects.filter(
                title=serializer.validated_data['title'],
                category=serializer.validated_data['category']
            ).exists():
                raise ValidationError("A course with this title already exists in this category")
            serializer.save(teacher=self.request.user)
            logger.info(f"Course created: {serializer.instance.title} by {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error creating course: {str(e)}")
            raise

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.select_related('course').all()
    serializer_class = ModuleSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['course']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'title', 'order']
    ordering = ['order']

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not course.is_active:
            raise ValidationError("Cannot create module for inactive course")
        if self.request.user.role == 'teacher' and course.teacher != self.request.user:
            raise ValidationError("You can only create modules for your own courses")
        serializer.save()

class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related('module').all()
    serializer_class = LessonSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['module', 'lesson_type']
    search_fields = ['title', 'content']
    ordering_fields = ['duration', 'order']
    ordering = ['order']

    def perform_create(self, serializer):
        module = serializer.validated_data['module']
        if not module.is_active:
            raise ValidationError("Cannot create lesson for inactive module")
        if self.request.user.role == 'teacher' and module.course.teacher != self.request.user:
            raise ValidationError("You can only create lessons for your own courses")
        serializer.save()

class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.select_related('lesson').all()
    serializer_class = AssignmentSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['lesson']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'title']
    ordering = ['due_date']

    def perform_create(self, serializer):
        lesson = serializer.validated_data['lesson']
        if not lesson.is_active:
            raise ValidationError("Cannot create assignment for inactive lesson")
        if self.request.user.role == 'teacher' and lesson.module.course.teacher != self.request.user:
            raise ValidationError("You can only create assignments for your own courses")
        serializer.save()

class SubmissionViewSet(viewsets.ModelViewSet):
    queryset = Submission.objects.select_related('assignment', 'student').all()
    serializer_class = SubmissionSerializer
    permission_classes = [IsStudent]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['assignment', 'student', 'status']
    ordering_fields = ['submission_date', 'status']
    ordering = ['-submission_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Submission.objects.filter(student=user)
        if user.role == 'teacher':
            return Submission.objects.filter(assignment__lesson__module__course__teacher=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        try:
            assignment = serializer.validated_data['assignment']
            if not assignment.is_active:
                raise ValidationError("Cannot submit to inactive assignment")
            if Submission.objects.filter(assignment=assignment, student=self.request.user).exists():
                raise ValidationError("You have already submitted this assignment")
            serializer.save(student=self.request.user)
            logger.info(f"Submission created for assignment {assignment.id} by {self.request.user.email}")
        except Exception as e:
            logger.error(f"Error creating submission: {str(e)}")
            raise

class EnrollmentViewSet(viewsets.ModelViewSet):
    queryset = Enrollment.objects.select_related('user', 'course').all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsStudent]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['user', 'course']
    ordering_fields = ['enrollment_date', 'progress']
    ordering = ['-enrollment_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Enrollment.objects.filter(user=user)
        if user.role == 'teacher':
            return Enrollment.objects.filter(course__teacher=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not course.is_active:
            raise ValidationError("Cannot enroll in inactive course")
        if Enrollment.objects.filter(course=course, user=self.request.user).exists():
            raise ValidationError("You are already enrolled in this course")
        serializer.save(user=self.request.user)

class LessonProgressViewSet(viewsets.ModelViewSet):
    queryset = LessonProgress.objects.select_related('user', 'lesson').all()
    serializer_class = LessonProgressSerializer
    permission_classes = [IsStudent]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['user', 'lesson', 'status']
    ordering_fields = ['completion_date', 'time_spent']
    ordering = ['-completion_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return LessonProgress.objects.filter(user=user)
        if user.role == 'teacher':
            return LessonProgress.objects.filter(lesson__module__course__teacher=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        lesson = serializer.validated_data['lesson']
        if not lesson.is_active:
            raise ValidationError("Cannot track progress for inactive lesson")
        serializer.save(user=self.request.user)

class CertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.select_related('user', 'course').all()
    serializer_class = CertificateSerializer
    permission_classes = [IsAdminOrTeacherOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_fields = ['user', 'course']
    ordering_fields = ['issue_date', 'certificate_number']
    ordering = ['-issue_date']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'student':
            return Certificate.objects.filter(user=user)
        if user.role == 'teacher':
            return Certificate.objects.filter(course__teacher=user)
        return super().get_queryset()

    def perform_create(self, serializer):
        course = serializer.validated_data['course']
        if not course.is_active:
            raise ValidationError("Cannot issue certificate for inactive course")
        if Certificate.objects.filter(course=course, user=self.request.user).exists():
            raise ValidationError("Certificate already exists for this course")
        serializer.save(user=self.request.user)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.select_related('sender', 'receiver').all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter)
    filterset_fields = ['sender', 'receiver', 'read_status']
    search_fields = ['content']
    ordering_fields = ['timestamp', 'read_status']
    ordering = ['-timestamp']

    def get_queryset(self):
        return Message.objects.filter(
            Q(sender=self.request.user) | Q(receiver=self.request.user)
        ).select_related('sender', 'receiver')

    def perform_create(self, serializer):
        receiver = serializer.validated_data['receiver']
        if receiver == self.request.user:
            raise ValidationError("Cannot send message to yourself")
        serializer.save(sender=self.request.user)
