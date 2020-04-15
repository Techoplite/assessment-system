# Generated by Django 3.0.4 on 2020-04-14 10:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assessment', '0003_remove_problem_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('correct_answers_number', models.IntegerField()),
                ('total_assessment_questions', models.IntegerField()),
                ('errors_number', models.IntegerField()),
                ('correct_answers_percentage', models.DecimalField(decimal_places=1, max_digits=3)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='assessment.Assessment')),
                ('student', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]