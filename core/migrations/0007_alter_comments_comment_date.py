# Generated by Django 5.2.3 on 2025-07-15 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_comments_comment_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comments',
            name='comment_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
