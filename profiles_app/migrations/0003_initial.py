# Generated by Django 5.2.3 on 2025-07-09 12:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('profiles_app', '0002_delete_profile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(default='', max_length=50)),
                ('last_name', models.CharField(default='', max_length=50)),
                ('location', models.CharField(default='', max_length=100)),
                ('tel', models.CharField(default='', max_length=20)),
                ('description', models.TextField(default='')),
                ('working_hours', models.CharField(default='', max_length=50)),
                ('type', models.CharField(choices=[('business', 'Business'), ('customer', 'Customer')], default='customer', max_length=20)),
                ('file', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
