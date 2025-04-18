from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat

def validate_file_size(file):
    max_size_kb = 2048

    if file.size > max_size_kb * 1024:
        raise ValidationError(f'File size must not exceed {filesizeformat(max_size_kb * 1024)}')