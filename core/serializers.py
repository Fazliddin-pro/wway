from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Assignment,
    Submission, Enrollment, LessonProgress, Certificate, Message
)
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    instructor = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description',
            'category', 'level', 'accessibility_features', 'created_at', 'instructor'
        ]
        read_only_fields = ['instructor']

    def validate_instructor(self, value):
            if value.profile.status == 'student':
                raise ValidationError("A course cannot be created by a user with 'student' status.")
            return value

class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())
    course_title = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'course', 'course_title', 'order', 'start_date', 'end_date']

    def get_course_title(self, obj):
        return str(obj.course) if obj.course else None

class LessonSerializer(serializers.ModelSerializer):
    module = ModuleSerializer(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'module',
            'lesson_type', 'duration', 'accessibility_features'
        ]

class AssignmentSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'title', 'description', 'due_date'
        ]

class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'student',
            'submitted_file', 'submission_date', 'status'
        ]

class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'course',
            'enrollment_date', 'progress', 'needs_accessibility_support'
        ]

class LessonProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'user', 'lesson',
            'status', 'completion_date', 'time_spent'
        ]

class CertificateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'user', 'course',
            'issue_date', 'certificate_number', 'accessibility_features'
        ]

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'receiver',
            'content', 'timestamp', 'read_status',
            'via_telegram', 'telegram_message_id'
        ]
