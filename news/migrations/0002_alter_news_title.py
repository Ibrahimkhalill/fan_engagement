# Generated by Django 5.2.3 on 2025-07-25 04:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
