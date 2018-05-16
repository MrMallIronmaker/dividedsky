# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-05-16 03:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gamehendge', '0005_auto_20170930_0629'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='phone_number',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='path',
            name='dest',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='dest_paths', to='gamehendge.Station'),
        ),
        migrations.AlterField(
            model_name='path',
            name='source',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='source_paths', to='gamehendge.Station'),
        ),
    ]
