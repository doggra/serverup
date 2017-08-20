# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-20 16:26
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PackageUpdate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('version', models.CharField(blank=True, max_length=255)),
                ('ignore', models.BooleanField(default=False)),
                ('package', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Package')),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('os', models.IntegerField(choices=[(0, 'Debian'), (1, 'Centos')], null=True)),
                ('ip', models.GenericIPAddressField(default='127.1.1.1')),
                ('ssh_port', models.IntegerField(default=22)),
                ('hostname', models.CharField(default='Unknown', max_length=255)),
                ('status', models.IntegerField(choices=[(0, 'UP TO DATE'), (1, 'UPDATES AVAILABLE'), (2, 'PENDING'), (3, 'INSTALL'), (4, 'ERROR')], default=3)),
                ('public_key', models.TextField(blank=True)),
                ('private_key', models.TextField(blank=True)),
                ('last_check', models.DateTimeField(blank=True, null=True)),
                ('auto_updates', models.BooleanField(default=True)),
                ('update_interval', models.PositiveIntegerField(default=24)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ServerGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('servers', models.ManyToManyField(blank=True, to='server.Server')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='packageupdate',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='server.Server'),
        ),
        migrations.AddField(
            model_name='packageupdate',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
