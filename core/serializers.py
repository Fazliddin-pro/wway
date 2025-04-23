from rest_framework import serializers
from .models import (
    Course, Module, Lesson, Assignment,
    Submission, Enrollment, LessonProgress, Certificate, Message
)
from users.serializers import UserSerializer
from users.models import User
import uuid

class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'category', 'level', 'image', 'accessibility_features', 'is_active', 'created_at', 'teacher']
        read_only_fields = ['id', 'created_at', 'teacher']

    def validate(self, attrs):
        if self.context['request'].user.role not in ['admin', 'teacher']:
            raise serializers.ValidationError("Only admins and teachers can create courses")
        return attrs

    def create(self, validated_data):
        validated_data['teacher'] = self.context['request'].user
        return super().create(validated_data)

class ModuleSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.filter(is_active=True), required=True)
    course_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Module
        fields = [
            'id', 'title', 'description', 'course',
            'course_title', 'order', 'start_date', 'end_date', 'is_active'
        ]
        read_only_fields = ['id', 'course_title']

    def get_course_title(self, obj):
        return str(obj.course) if obj.course else None

    def validate(self, data):
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise serializers.ValidationError("Start date cannot be later than end date")
        course = data.get('course')
        if course and not course.is_active:
            raise serializers.ValidationError("Cannot create module for inactive course")
        return data

class LessonSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Module.objects.filter(is_active=True), required=True)
    module_title = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'title', 'content', 'module', 'module_title',
            'order', 'lesson_type', 'duration', 'accessibility_features', 'is_active'
        ]
        read_only_fields = ['id', 'module_title']

    def get_module_title(self, obj):
        return str(obj.module) if obj.module else None

    def validate(self, data):
        if 'order' in data:
            module = data.get('module', self.instance.module if self.instance else None)
            if module:
                if not module.is_active:
                    raise serializers.ValidationError("Cannot create lesson for inactive module")
                existing_lessons = Lesson.objects.filter(module=module).exclude(id=self.instance.id if self.instance else None)
                if existing_lessons.filter(order=data['order']).exists():
                    raise serializers.ValidationError("A lesson with this order already exists in this module")
        return data

class AssignmentSerializer(serializers.ModelSerializer):
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.filter(is_active=True), required=True)

    class Meta:
        model = Assignment
        fields = ['id', 'lesson', 'title', 'description', 'due_date', 'is_active']
        read_only_fields = ['id']

    def validate(self, data):
        lesson = data.get('lesson')
        if lesson and not lesson.is_active:
            raise serializers.ValidationError("Cannot create assignment for inactive lesson")
        return data

class SubmissionSerializer(serializers.ModelSerializer):
    assignment = serializers.PrimaryKeyRelatedField(queryset=Assignment.objects.filter(is_active=True), required=True)
    student = UserSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'submitted_file', 'submission_date', 'status']
        read_only_fields = ['id', 'submission_date', 'student']

    def validate(self, data):
        if Submission.objects.filter(
            student=self.context['request'].user,
            assignment=data['assignment']
        ).exists():
            raise serializers.ValidationError("You have already submitted this assignment")
        return data

class EnrollmentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.filter(is_active=True), required=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'user', 'course', 'enrollment_date', 'progress', 'needs_accessibility_support']
        read_only_fields = ['id', 'enrollment_date', 'user']

    def validate(self, data):
        course = data.get('course')
        if course and not course.is_active:
            raise serializers.ValidationError("Cannot enroll in inactive course")
        return data

class LessonProgressSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.filter(is_active=True), required=True)

    class Meta:
        model = LessonProgress
        fields = ['id', 'user', 'lesson', 'status', 'completion_date', 'time_spent']
        read_only_fields = ['id', 'user']

    def validate(self, data):
        lesson = data.get('lesson')
        if lesson and not lesson.is_active:
            raise serializers.ValidationError("Cannot track progress for inactive lesson")
        return data

class CertificateSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'user', 'course', 'issue_date', 'certificate_number', 'accessibility_features']
        read_only_fields = ['user', 'issue_date', 'certificate_number']

    def validate(self, attrs):
        course = attrs.get('course')
        if not course.is_active:
            raise serializers.ValidationError("Cannot create certificate for inactive course")
            
        if Certificate.objects.filter(course=course, user=self.context['request'].user).exists():
            raise serializers.ValidationError("Certificate already exists for this course")
            
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        validated_data['certificate_number'] = f"CRT-{uuid.uuid4().hex[:8].upper()}"
        return super().create(validated_data)

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'read_status', 'via_telegram', 'telegram_message_id']
        read_only_fields = ['id', 'timestamp', 'sender']

    def validate(self, data):
        if data['receiver'] == self.context['request'].user:
            raise serializers.ValidationError("You cannot send a message to yourself")
        return data

