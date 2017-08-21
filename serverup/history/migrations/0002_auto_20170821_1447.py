# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-21 14:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('history', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event_type',
            field=models.IntegerField(choices=[(0, 'SSH command sent'), (1, 'Server added')], default=0),
        ),
        migrations.AlterField(
            model_name='event',
            name='info',
            field=models.TextField(default=''),
        ),
    ]
