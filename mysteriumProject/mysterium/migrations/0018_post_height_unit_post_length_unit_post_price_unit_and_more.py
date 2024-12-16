# Generated by Django 5.1.2 on 2024-12-16 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mysterium', '0017_remove_post_height_unit_remove_post_length_unit_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='height_unit',
            field=models.CharField(choices=[('cm', 'Centimeter'), ('m', 'Meter'), ('kg', 'Kilogram'), ('g', 'Gram'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='cm', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='length_unit',
            field=models.CharField(choices=[('cm', 'Centimeter'), ('m', 'Meter'), ('kg', 'Kilogram'), ('g', 'Gram'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='cm', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='price_unit',
            field=models.CharField(choices=[('cm', 'Centimeter'), ('m', 'Meter'), ('kg', 'Kilogram'), ('g', 'Gram'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='USD', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='weight_unit',
            field=models.CharField(choices=[('cm', 'Centimeter'), ('m', 'Meter'), ('kg', 'Kilogram'), ('g', 'Gram'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='g', max_length=10),
        ),
        migrations.AddField(
            model_name='post',
            name='width_unit',
            field=models.CharField(choices=[('cm', 'Centimeter'), ('m', 'Meter'), ('kg', 'Kilogram'), ('g', 'Gram'), ('USD', 'US Dollar'), ('EUR', 'Euro')], default='cm', max_length=10),
        ),
    ]
