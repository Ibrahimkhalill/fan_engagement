# Generated by Django 5.2.3 on 2025-07-28 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('match', '0006_match_match_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='points_calculated',
            field=models.BooleanField(default=False),
        ),
    ]
