# Generated by Django 5.2 on 2025-04-12 10:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_alter_user_options_user_created_at_user_updated_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='is_teacher',
        ),
    ]
