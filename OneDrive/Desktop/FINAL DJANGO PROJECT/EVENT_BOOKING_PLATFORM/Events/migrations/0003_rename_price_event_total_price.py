# Generated by Django 5.0.2 on 2024-12-08 21:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Events', '0002_booking_total_price_event_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='price',
            new_name='total_price',
        ),
    ]
