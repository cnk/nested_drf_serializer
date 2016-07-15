# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='GoalPrerequisite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('child', models.ForeignKey(related_name='prerequisites', to='project.Goal', db_column='child_key')),
                ('parent', models.ForeignKey(related_name='dependants', to='project.Goal', db_column='parent_key')),
            ],
        ),
        migrations.CreateModel(
            name='MetaGoal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='MetaGoalPrerequisite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('child', models.ForeignKey(related_name='mg_prerequisites', to='project.MetaGoal', db_column='child_key')),
                ('parent', models.ForeignKey(related_name='mg_dependants', to='project.MetaGoal', db_column='parent_key')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='metagoal',
            name='project',
            field=models.ForeignKey(related_name='metagoals', to='project.Project'),
        ),
        migrations.AddField(
            model_name='goal',
            name='metagoal',
            field=models.ForeignKey(related_name='goals', to='project.MetaGoal'),
        ),
        migrations.AlterUniqueTogether(
            name='metagoalprerequisite',
            unique_together=set([('parent', 'child')]),
        ),
        migrations.AlterUniqueTogether(
            name='goalprerequisite',
            unique_together=set([('parent', 'child')]),
        ),
    ]
