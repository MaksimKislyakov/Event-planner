# Generated by Django 5.1.4 on 2025-04-27 11:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('project', '0003_project_parent_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='parent_project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_projects', to='project.project', verbose_name='Родительский проект'),
        ),
    ]
