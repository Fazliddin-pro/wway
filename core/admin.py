from django.contrib import admin
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)

# Inline для модулей внутри курса
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('order', 'title', 'start_date', 'end_date')
    readonly_fields = ()

# Inline для уроков внутри модуля
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('order', 'title', 'lesson_type', 'duration')
    readonly_fields = ()

# Inline для заданий внутри урока
class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('title', 'due_date')
    readonly_fields = ()

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'instructor', 'category', 'level', 'created_at')
    list_filter = ('category', 'level')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    list_editable = ('category', 'level')
    inlines = [ModuleInline]

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'start_date', 'end_date')
    list_filter = ('course',)
    search_fields = ('title', 'description')
    ordering = ('course', 'order')
    list_editable = ('order', 'start_date', 'end_date')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module', 'order', 'lesson_type', 'duration')
    list_filter = ('module', 'lesson_type')
    search_fields = ('title', 'content')
    ordering = ('module', 'order')
    list_editable = ('order', 'lesson_type', 'duration')
    inlines = [AssignmentInline]

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'lesson', 'due_date')
    list_filter = ('lesson',)
    search_fields = ('title', 'description')
    ordering = ('lesson', 'due_date')
    list_editable = ('due_date',)

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'student', 'submission_date', 'status')
    list_filter = ('assignment', 'status')
    search_fields = ('status',)
    ordering = ('-submission_date',)
    list_editable = ('status',)

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'enrollment_date', 'progress', 'needs_accessibility_support')
    list_filter = ('course', 'needs_accessibility_support')
    search_fields = ('user__email', 'course__title')
    ordering = ('-enrollment_date',)
    list_editable = ('progress', 'needs_accessibility_support')

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'status', 'completion_date', 'time_spent')
    list_filter = ('status', 'lesson')
    search_fields = ('user__email',)
    ordering = ('user', 'lesson')
    list_editable = ('status', 'time_spent')

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'issue_date', 'certificate_number')
    list_filter = ('course', 'issue_date')
    search_fields = ('user__email', 'certificate_number')
    ordering = ('-issue_date',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'read_status', 'via_telegram')
    list_filter = ('read_status', 'via_telegram')
    search_fields = ('content',)
    ordering = ('-timestamp',)
    list_editable = ('read_status', 'via_telegram')
