# Generated by Django 2.2.11 on 2020-05-05 20:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dgf', '0021_auto_20200503_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ace',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aces',
                                    to='dgf.Course', verbose_name='Course'),
        ),
        migrations.AlterField(
            model_name='ace',
            name='disc',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='aces',
                                    to='dgf.Disc', verbose_name='Disc'),
        ),
        migrations.AlterField(
            model_name='discinbag',
            name='disc',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bags', to='dgf.Disc',
                                    verbose_name='Disc'),
        ),
        migrations.AlterField(
            model_name='discinbag',
            name='friend',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discs', to='dgf.Friend',
                                    verbose_name='Player'),
        ),
    ]
