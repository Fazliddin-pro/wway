from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Assignment,
    Submission, Enrollment, LessonProgress, Certificate, Message
)
from users.serializers import UserSerializer

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description',
            'category', 'level', 'accessibility_features',
            'created_at', 'teacher'
        ]
        read_only_fields = ['id', 'created_at', 'teacher']

    def validate(self, data):
        if self.instance and 'teacher' in data:
            if data['teacher'].role not in ['admin', 'teacher']:
                raise serializers.ValidationError("Only admins or teachers can create courses")
        return data

class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=True)
    course_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'course',
            'course_title', 'order', 'start_date', 'end_date'
        ]
        read_only_fields = ['id', 'course_title']

    def get_course_title(self, obj):
        return str(obj.course) if obj.course else None

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Start date cannot be later than end date")
        return data

class LessonSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.all(), required=True)
    module_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'module', 'module_title',
            'order', 'lesson_type', 'duration', 'accessibility_features'
        ]
        read_only_fields = ['id', 'module_title']

    def get_module_title(self, obj):
        return str(obj.module) if obj.module else None

    def validate(self, data):
        if 'order' in data:
            module = data.get('module', self.instance.module if self.instance else None)
            if module:
                existing_lessons = Lesson.objects.filter(module=module).exclude(id=self.instance.id if self.instance else None)
                if existing_lessons.filter(order=data['order']).exists():
                    raise serializers.ValidationError("A lesson with this order already exists in this module")
        return data

class AssignmentSerializer(serializers.ModelSerializer):
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = Assignment
        fields = [
            'id', 'lesson', 'title', 'description', 'due_date'
        ]
        read_only_fields = ['id']

class SubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'student',
            'submitted_file', 'submission_date', 'status'
        ]
        read_only_fields = ['id', 'submission_date']

class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = [
            'id', 'user', 'course',
            'enrollment_date', 'progress', 'needs_accessibility_support'
        ]
        read_only_fields = ['id', 'enrollment_date']

class LessonProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    lesson = LessonSerializer(read_only=True)

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'user', 'lesson',
            'status', 'completion_date', 'time_spent'
        ]
        read_only_fields = ['id']

class CertificateSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = [
            'id', 'user', 'course',
            'issue_date', 'certificate_number', 'accessibility_features'
        ]
        read_only_fields = ['id', 'issue_date']

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
        read_only_fields = ['id', 'timestamp']
