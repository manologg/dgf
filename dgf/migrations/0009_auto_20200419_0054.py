# Generated by Django 2.2.11 on 2020-04-18 22:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dgf', '0008_auto_20200417_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='division',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='dgf.Division'),
        ),
    ]