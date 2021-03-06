# Generated by Django 2.0.1 on 2018-01-26 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('burnDownBackEnd', '0003_auto_20180125_2303'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pbi',
            name='pbitype',
            field=models.CharField(choices=[('NEW', 'NEW'), ('ACTIVE', 'Active'), ('OPEN', 'Open'), ('RESOLVED', 'Resolved'), ('CLOSED', 'Closed.')], max_length=20),
        ),
        migrations.AlterField(
            model_name='pbi',
            name='state',
            field=models.CharField(choices=[('BUG', 'Bug'), ('US', 'User Story')], max_length=20),
        ),
        migrations.DeleteModel(
            name='PbiType',
        ),
        migrations.DeleteModel(
            name='State',
        ),
    ]
