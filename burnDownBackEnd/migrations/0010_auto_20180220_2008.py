# Generated by Django 2.0.1 on 2018-02-21 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('burnDownBackEnd', '0009_auto_20180220_2006'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pbi',
            old_name='is_interuption',
            new_name='is_interruption',
        ),
    ]
