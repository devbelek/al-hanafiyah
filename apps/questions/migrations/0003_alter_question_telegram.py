# Generated by Django 5.0 on 2025-01-17 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questions', '0002_alter_answer_content_alter_question_content'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='telegram',
            field=models.CharField(blank=True, max_length=100, verbose_name='Telegram'),
        ),
    ]
