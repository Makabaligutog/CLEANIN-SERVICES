# Generated by Django 5.0.4 on 2025-01-09 02:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cleaning', '0003_remove_rating_user_alter_rating_id'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
