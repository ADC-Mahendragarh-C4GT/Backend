# Generated by Django 5.2.3 on 2025-07-06 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(choices=[('JE', 'Junior Engineer'), ('AE', 'Assistant Engineer'), ('XEN', 'Executive Engineer'), ('SE', 'Superintending Engineer'), ('CE', 'Chief Engineer'), ('JCMC', 'Joint Commissioner, Municipal Corporation'), ('CMC', 'Commissioner, Municipal Corporation')], default='other', max_length=20),
        ),
    ]
