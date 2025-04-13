from django.core.exceptions import ValidationError

def validate_avatar_size(file):
    max_size_kb = 1024
    if file.size > max_size_kb * 1024:
        raise ValidationError(f'Avatar file size must be less than {max_size_kb} KB')