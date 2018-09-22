# Generated by Django 2.0.7 on 2018-09-22 02:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('edensystem', '0002_auto_20180922_1038'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='image',
            new_name='thumbnail',
        ),
        migrations.AddField(
            model_name='profile',
            name='sex',
            field=models.CharField(choices=[('male', 'male'), ('female', 'female')], default='male', max_length=5, verbose_name='gender'),
        ),
    ]