# Generated by Django 5.0 on 2025-01-16 22:53

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_remove_offlineevent_additional_info_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='offlineevent',
            name='description',
            field=ckeditor.fields.RichTextField(verbose_name='Описание'),
        ),
    ]
