# Generated by Django 5.0.4 on 2025-01-08 08:45

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('image', models.ImageField(upload_to='services_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceReview',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customer_name', models.CharField(max_length=100)),
                ('message', models.TextField()),
                ('photo', models.ImageField(upload_to='service_photos/')),
                ('rating', models.PositiveIntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
            ],
        ),
        migrations.CreateModel(
            name='Booking',
            fields=[
                ('booking_id', models.AutoField(editable=False, primary_key=True, serialize=False)),
                ('cleaning_service', models.CharField(choices=[('residential', 'Residential Cleaning'), ('commercial', 'Commercial Cleaning'), ('move-in-out', 'Move-in/Move-out Cleaning'), ('carpet-cleaning', 'Carpet Cleaning'), ('window-cleaning', 'Window Cleaning'), ('eco-friendly', 'Eco-friendly Green Cleaning'), ('anti-bacterial-mist', 'Anti-Bacterial Mist Treatment'), ('car-interior-detailing', 'Car Interior Detailing'), ('deep-dry-cleaning', 'Deep Dry Cleaning'), ('deep-home-cleaning', 'Deep Home Cleaning'), ('deep-upholstery-shampooing', 'Deep Upholstery Shampooing'), ('steam-sterilization', 'Superior Steam Sterilization')], max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(default='Unknown', max_length=100)),
                ('contact_number', models.CharField(max_length=15)),
                ('address', models.TextField()),
                ('additional_info', models.TextField(blank=True, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('booking_date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ServiceRating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_name', models.CharField(choices=[('residential', 'Residential Cleaning'), ('commercial', 'Commercial Cleaning'), ('deep-cleaning', 'Deep Cleaning'), ('move-in-out', 'Move-in/Move-out Cleaning'), ('carpet-cleaning', 'Carpet Cleaning'), ('upholstery-cleaning', 'Upholstery Cleaning'), ('window-cleaning', 'Window Cleaning'), ('eco-friendly', 'Eco-friendly Green Cleaning'), ('anti-bacterial-mist', 'Anti-Bacterial Mist Treatment'), ('car-interior-detailing', 'Car Interior Detailing'), ('deep-dry-cleaning', 'Deep Dry Cleaning'), ('deep-home-cleaning', 'Deep Home Cleaning'), ('deep-upholstery-shampooing', 'Deep Upholstery Shampooing'), ('steam-sterilization', 'Superior Steam Sterilization')], max_length=50)),
                ('rating', models.IntegerField()),
                ('month', models.CharField(max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'service_name', 'month')},
            },
        ),
    ]
