# Generated by Django 3.2.15 on 2022-09-29 13:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_otp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='otp',
            old_name='mobile',
            new_name='phone',
        ),
    ]