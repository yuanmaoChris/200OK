# Generated by Django 2.1.5 on 2020-03-07 03:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20200306_2323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='avatar',
            field=models.ImageField(blank=True, default='avatar/default-avatar.png', null=True, upload_to='avatar/'),
        ),
        migrations.AlterField(
            model_name='author',
            name='id',
            field=models.CharField(default='443d898c-ce11-425a-a85b-c7f4f17fdc22', editable=False, max_length=100, primary_key=True, serialize=False, unique=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='url',
            field=models.URLField(default='443d898c-ce11-425a-a85b-c7f4f17fdc22', max_length=100),
        ),
    ]