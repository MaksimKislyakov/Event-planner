# Generated by Django 5.1.1 on 2024-11-19 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectfile',
            name='file_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]