# Generated by Django 3.0.4 on 2020-04-14 10:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assessment', '0002_problem_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='problem',
            name='number',
        ),
    ]
