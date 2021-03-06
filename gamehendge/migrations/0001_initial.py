# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-15 06:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import gamehendge.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Mook',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mook_type', models.IntegerField()),
                ('team', models.IntegerField()),
                ('launch_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Path',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('energy', models.IntegerField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_type', models.IntegerField(choices=[(1, b'energy'), (2, b'shooters'), (3, b'lightning')], default=gamehendge.models.StationType(1))),
                ('team', models.IntegerField(choices=[(1, b'red'), (2, b'blue')])),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamehendge.Player')),
                ('target', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='gamehendge.Station')),
            ],
        ),
        migrations.AddField(
            model_name='path',
            name='dest',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='dest_paths', to='gamehendge.Station'),
        ),
        migrations.AddField(
            model_name='path',
            name='source',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='source_paths', to='gamehendge.Station'),
        ),
        migrations.AddField(
            model_name='mook',
            name='path',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gamehendge.Path'),
        ),
    ]
