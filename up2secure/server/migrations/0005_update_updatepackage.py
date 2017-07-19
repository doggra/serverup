# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-18 21:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0004_auto_20170714_1548'),
    ]

    operations = [
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Server')),
            ],
        ),
        migrations.CreateModel(
            name='UpdatePackage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('package_name', models.CharField(max_length=256)),
                ('update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Update')),
            ],
        ),
    ]
