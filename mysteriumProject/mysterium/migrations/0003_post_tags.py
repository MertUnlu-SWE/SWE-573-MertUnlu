# Generated by Django 5.1.2 on 2024-10-28 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysterium', '0002_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags.', max_length=500),
        ),
    ]
