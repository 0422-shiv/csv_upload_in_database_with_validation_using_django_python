# Generated by Django 3.2.7 on 2021-10-05 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Institutions',
            fields=[
                ('institution_id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'institutions',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('update_at', models.DateTimeField(auto_now=True, null=True)),
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(blank=True, db_index=True, max_length=25, null=True, unique=True)),
                ('email', models.EmailField(db_index=True, max_length=254, unique=True)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('first_name', models.CharField(blank=True, default=None, max_length=35, null=True)),
                ('last_name', models.CharField(blank=True, default=None, max_length=35, null=True)),
                ('city', models.CharField(blank=True, default=None, max_length=35, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, default=None, max_length=2, null=True)),
                ('is_terms_conditions', models.BooleanField(default=False)),
                ('profile_image', models.ImageField(blank=True, default=None, null=True, upload_to='Avatar')),
                ('sign_in_counts', models.SmallIntegerField(default=0)),
                ('redirect_url', models.CharField(blank=True, max_length=255, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_requests_created', to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('institution_id', models.ForeignKey(blank=True, db_column='institution_id', null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.institutions')),
                ('update_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_requests_updated', to=settings.AUTH_USER_MODEL)),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
