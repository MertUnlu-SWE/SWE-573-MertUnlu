# Generated by Django 5.1.2 on 2024-11-21 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysterium', '0005_comment_downvotes_comment_upvotes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_solved',
            field=models.BooleanField(default=False),
        ),
    ]
