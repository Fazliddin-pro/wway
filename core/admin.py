from django.contrib import admin
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'category', 'level', 'created_at')
    list_filter = ('category', 'level')
    search_fields = ('title', 'description')

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'start_date', 'end_date')
    list_filter = ('course',)
    search_fields = ('title', 'description')

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module', 'lesson_type', 'duration')
    list_filter = ('module', 'lesson_type')
    search_fields = ('title', 'content')

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'lesson', 'due_date')
    list_filter = ('lesson',)
    search_fields = ('title', 'description')

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'student', 'submission_date', 'status')
    list_filter = ('assignment', 'status')
    search_fields = ('status',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'enrollment_date', 'progress', 'needs_accessibility_support')
    list_filter = ('course', 'needs_accessibility_support')
    search_fields = ('user__email', 'course__title')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'status', 'completion_date', 'time_spent')
    list_filter = ('status', 'lesson')
    search_fields = ('user__email',)

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'issue_date', 'certificate_number')
    list_filter = ('course', 'issue_date')
    search_fields = ('user__email', 'certificate_number')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'read_status', 'via_telegram')
    list_filter = ('read_status', 'via_telegram')
    search_fields = ('content',)
