# Generated by Django 2.2.11 on 2020-04-10 23:21

from decimal import Decimal

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('dgf', '0004_auto_20200407_1319'),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='free_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='friend',
            name='plays_since',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              validators=[django.core.validators.MinValueValidator(1926)]),
        ),
        migrations.AlterField(
            model_name='friend',
            name='pdga_number',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='friend',
            name='rating',
            field=models.PositiveIntegerField(blank=True, null=True,
                                              validators=[django.core.validators.MaxValueValidator(2000)]),
        ),
        migrations.AlterField(
            model_name='friend',
            name='total_earnings',
            field=models.DecimalField(decimal_places=2, default=Decimal('0'), max_digits=10),
        ),
        migrations.AlterField(
            model_name='friend',
            name='total_tournaments',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
        migrations.CreateModel(
            name='Highlight',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=100)),
                ('friend', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dgf.Friend')),
            ],
        ),
    ]
