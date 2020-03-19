# Generated by Django 2.1.5 on 2020-03-19 06:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('email', models.EmailField(max_length=60, unique=True, verbose_name='email address')),
                ('id', models.CharField(default='a6d1258d-b1b8-4c80-9c05-b1793c81e39c', editable=False, max_length=100, primary_key=True, serialize=False, unique=True)),
                ('displayName', models.CharField(max_length=30)),
                ('lastName', models.CharField(blank=True, max_length=30)),
                ('firstName', models.CharField(blank=True, max_length=30)),
                ('host', models.CharField(default='127.0.0.1:8000', max_length=100)),
                ('url', models.CharField(default='', max_length=100)),
                ('avatar', models.ImageField(blank=True, default='avatar/default-avatar.png', null=True, upload_to='avatar/')),
                ('github', models.URLField(default='', max_length=100, null=True)),
                ('bio', models.CharField(default='This guy is too lazy to write a bio...', max_length=200, null=True)),
                ('date_joined', models.DateField(auto_now=True, verbose_name='date joined')),
                ('last_login', models.DateField(auto_now=True, verbose_name='last login')),
                ('active', models.BooleanField(default=True)),
                ('activated', models.BooleanField(default=False)),
                ('admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
