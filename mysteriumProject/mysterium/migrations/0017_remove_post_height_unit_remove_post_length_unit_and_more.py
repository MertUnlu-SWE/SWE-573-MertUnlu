# Generated by Django 5.1.2 on 2024-12-16 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mysterium', '0016_post_height_unit_post_length_unit_post_price_unit_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='height_unit',
        ),
        migrations.RemoveField(
            model_name='post',
            name='length_unit',
        ),
        migrations.RemoveField(
            model_name='post',
            name='price_unit',
        ),
        migrations.RemoveField(
            model_name='post',
            name='weight_unit',
        ),
        migrations.RemoveField(
            model_name='post',
            name='width_unit',
        ),
    ]
