from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from .validators import validate_file_size

LESSON_TYPES = [('video', 'Video'), ('text', 'Text')]
SUBMISSION_STATUSES = [('not_looked', 'Not Looked'), ('in_progress', 'In Progress'), ('looked', 'Looked')]
PROGRESS_STATUSES = [('not_started', 'Not Started'), ('in_progress', 'In Progress'), ('completed', 'Completed')]

class Course(models.Model):
    title = models.CharField("Course Title", max_length=255)
    description = models.TextField("Course Description")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Teacher")
    category = models.CharField("Category", max_length=100)
    level = models.CharField("Level", max_length=50, blank=True, null=True)
    image = models.ImageField("Course Image", upload_to='course_images/', blank=True, null=True)
    accessibility_features = models.TextField("Accessibility Features", blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)
    created_at = models.DateTimeField("Created At", auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def clean(self):
        super().clean()
        if not getattr(self.teacher, 'role', None) in ['admin', 'teacher']:
            raise ValidationError("Only admins or teachers can create a course.")

    def __str__(self):
        return f'{self.category} - {self.title} ({self.level})'

class Module(models.Model):
    title = models.CharField("Module Title", max_length=255)
    description = models.TextField("Module Description")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules', verbose_name="Course")
    order = models.PositiveSmallIntegerField("Order", default=1, validators=[MinValueValidator(1)])
    start_date = models.DateField("Start Date", blank=True, null=True)
    end_date = models.DateField("End Date", blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        unique_together = ('course', 'order')

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError("Start date cannot be later than end date.")

    def __str__(self):
        return f'{self.course} - {self.order}. {self.title}'

class Lesson(models.Model):
    title = models.CharField("Lesson Title", max_length=255)
    content = models.TextField("Content")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons', verbose_name="Module")
    order = models.PositiveSmallIntegerField("Order", default=1, validators=[MinValueValidator(1)])
    lesson_type = models.CharField("Lesson Type", max_length=10, choices=LESSON_TYPES, default='text')
    duration = models.IntegerField("Duration (minutes)", blank=True, null=True)
    accessibility_features = models.TextField("Accessibility Features", blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ['order']
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        unique_together = ('module', 'order')

    def __str__(self):
        return f'{self.module} - {self.order}. {self.title}'

class Assignment(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='assignments', verbose_name="Lesson")
    title = models.CharField("Assignment Title", max_length=255)
    description = models.TextField("Assignment Description")
    due_date = models.DateField("Due Date", blank=True, null=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        verbose_name = "Assignment"
        verbose_name_plural = "Assignments"

    def __str__(self):
        return f'{self.lesson} - {self.title} ({self.due_date})'

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name="Assignment")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions', verbose_name="Student")
    submitted_file = models.FileField("Submitted File", upload_to='submissions/', validators=[validate_file_size])
    submission_date = models.DateTimeField("Submission Date", auto_now_add=True)
    status = models.CharField("Submission Status", max_length=15, choices=SUBMISSION_STATUSES, default='not_looked')
    
    class Meta:
        ordering = ['-submission_date']
        verbose_name = "Submission"
        verbose_name_plural = "Submissions"

    def __str__(self):
        return f"Submission {self.id} is {self.status}"

class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', verbose_name="User")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="Course")
    enrollment_date = models.DateTimeField("Enrollment Date", auto_now_add=True)
    progress = models.PositiveSmallIntegerField("Progress (%)", default=0)
    needs_accessibility_support = models.BooleanField("Needs Accessibility Support", default=False)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"

    def __str__(self):
        return f"{self.user} enrolled in {self.course}"

class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progresses', verbose_name="User")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='progresses', verbose_name="Lesson")
    status = models.CharField("Progress Status", max_length=15, choices=PROGRESS_STATUSES, default='not_started')
    completion_date = models.DateTimeField("Completion Date", blank=True, null=True)
    time_spent = models.PositiveSmallIntegerField("Time Spent (minutes)", blank=True, null=True)

    class Meta:
        unique_together = ('user', 'lesson')
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progresses"

    def __str__(self):
        return f"{self.user} progress on {self.lesson}"

class Certificate(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates', verbose_name="User")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', verbose_name="Course")
    issue_date = models.DateTimeField("Issue Date", auto_now_add=True)
    certificate_number = models.CharField("Certificate Number", max_length=100, unique=True)
    accessibility_features = models.TextField("Accessibility Features", blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"Certificate {self.certificate_number}"

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_messages', on_delete=models.CASCADE, verbose_name="Sender")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE, verbose_name="Receiver")
    content = models.TextField("Message Content")
    timestamp = models.DateTimeField("Timestamp", auto_now_add=True)
    read_status = models.BooleanField("Read Status", default=False)
    via_telegram = models.BooleanField("Via Telegram", default=False)
    telegram_message_id = models.CharField("Telegram Message ID", max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['timestamp']
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"
