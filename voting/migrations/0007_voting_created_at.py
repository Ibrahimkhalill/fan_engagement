# Generated by Django 5.2.3 on 2025-07-28 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('voting', '0006_alter_voting_goal_difference_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='voting',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
