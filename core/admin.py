from django.contrib import admin
from .models import (
    Course, Module, Lesson, Assignment, Submission,
    Enrollment, LessonProgress, Certificate, Message
)

# Inline for modules within course
class ModuleInline(admin.TabularInline):
    model = Module
    extra = 0
    fields = ('order', 'title', 'description', 'start_date', 'end_date', 'is_active')
    readonly_fields = ()
    show_change_link = True

# Inline for lessons within module
class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0
    fields = ('order', 'title', 'lesson_type', 'duration', 'content', 'accessibility_features', 'is_active')
    readonly_fields = ()
    show_change_link = True

# Inline for assignments within lesson
class AssignmentInline(admin.TabularInline):
    model = Assignment
    extra = 0
    fields = ('title', 'description', 'due_date', 'is_active')
    readonly_fields = ()
    show_change_link = True

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'teacher', 'category', 'level', 'image', 'is_active', 'created_at')
    list_filter = ('teacher', 'category', 'level', 'is_active', 'created_at')
    search_fields = ('id', 'title', 'description', 'category', 'level')
    ordering = ('-created_at',)
    list_editable = ('category', 'level', 'is_active', 'image')
    inlines = [ModuleInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'teacher', 'image')
        }),
        ('Additional Information', {
            'fields': ('category', 'level', 'accessibility_features', 'is_active')
        }),
    )

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'course', 'order', 'start_date', 'end_date', 'is_active')
    list_filter = ('course', 'is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description', 'course__title')
    ordering = ('course', 'order')
    list_editable = ('order', 'start_date', 'end_date', 'is_active')
    inlines = [LessonInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'course')
        }),
        ('Additional Information', {
            'fields': ('order', 'start_date', 'end_date', 'is_active')
        }),
    )

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'module', 'order', 'lesson_type', 'duration', 'is_active')
    list_filter = ('module', 'lesson_type', 'is_active')
    search_fields = ('title', 'content', 'module__title')
    ordering = ('module', 'order')
    list_editable = ('order', 'lesson_type', 'duration', 'is_active')
    inlines = [AssignmentInline]
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'content', 'module')
        }),
        ('Additional Information', {
            'fields': ('order', 'lesson_type', 'duration', 'accessibility_features', 'is_active')
        }),
    )

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'lesson', 'due_date', 'is_active')
    list_filter = ('lesson', 'is_active', 'due_date')
    search_fields = ('title', 'description', 'lesson__title')
    ordering = ('lesson', 'due_date')
    list_editable = ('due_date', 'is_active')
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'lesson')
        }),
        ('Additional Information', {
            'fields': ('due_date', 'is_active')
        }),
    )

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'assignment', 'student', 'submission_date', 'status', 'submitted_file')
    list_filter = ('assignment', 'status', 'submission_date')
    search_fields = ('status', 'student__email', 'assignment__title')
    ordering = ('-submission_date',)
    list_editable = ('status',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('assignment', 'student', 'submitted_file')
        }),
        ('Additional Information', {
            'fields': ('status', 'submission_date')
        }),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'enrollment_date', 'progress', 'needs_accessibility_support')
    list_filter = ('course', 'needs_accessibility_support', 'enrollment_date')
    search_fields = ('user__email', 'course__title')
    ordering = ('-enrollment_date',)
    list_editable = ('progress', 'needs_accessibility_support')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'course')
        }),
        ('Additional Information', {
            'fields': ('progress', 'needs_accessibility_support', 'enrollment_date')
        }),
    )

@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'lesson', 'status', 'completion_date', 'time_spent')
    list_filter = ('status', 'lesson', 'completion_date')
    search_fields = ('user__email', 'lesson__title')
    ordering = ('user', 'lesson')
    list_editable = ('status', 'time_spent')
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'lesson')
        }),
        ('Additional Information', {
            'fields': ('status', 'completion_date', 'time_spent')
        }),
    )

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'course', 'issue_date', 'certificate_number')
    list_filter = ('course', 'issue_date')
    search_fields = ('user__email', 'certificate_number', 'course__title')
    ordering = ('-issue_date',)
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'course', 'certificate_number')
        }),
        ('Additional Information', {
            'fields': ('issue_date', 'accessibility_features')
        }),
    )

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'read_status', 'via_telegram', 'telegram_message_id')
    list_filter = ('read_status', 'via_telegram', 'timestamp')
    search_fields = ('content', 'sender__email', 'receiver__email')
    ordering = ('-timestamp',)
    list_editable = ('read_status', 'via_telegram')
    fieldsets = (
        ('Basic Information', {
            'fields': ('sender', 'receiver', 'content')
        }),
        ('Additional Information', {
            'fields': ('read_status', 'via_telegram', 'telegram_message_id', 'timestamp')
        }),
    )
