# Generated by Django 2.0.1 on 2018-01-31 03:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burnDownBackEnd', '0005_auto_20180130_2205'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pbi',
            name='pbitype',
            field=models.CharField(choices=[('BUG', 'Bug'), ('US', 'User Story')], max_length=20),
        ),
        migrations.AlterField(
            model_name='pbi',
            name='state',
            field=models.CharField(choices=[('NEW', 'New'), ('ACTIVE', 'Active'), ('OPEN', 'Open'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed')], max_length=20),
        ),
    ]
