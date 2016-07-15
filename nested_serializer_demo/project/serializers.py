from rest_framework import serializers
from .models import Project, MetaGoal, MetaGoalPrerequisite, Goal, GoalPrerequisite


class GoalPrerequisiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = GoalPrerequisite
        fields = ('id', 'url', 'parent', 'child')


class GoalSerializer(serializers.HyperlinkedModelSerializer):
    metagoal_name = serializers.CharField(source='metagoal.name')

    class Meta:
        model = Goal
        fields = ('id', 'url', 'name', 'metagoal', 'metagoal_name')


class MetaGoalPrerequisiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MetaGoalPrerequisite
        fields = ('id', 'url')


class MetaGoalSerializer(serializers.HyperlinkedModelSerializer):
    goals = GoalSerializer(many=True, read_only=True)
    project_name = serializers.CharField(source='project.name')

    class Meta:
        model = MetaGoal
        fields = ('id', 'url', 'name', 'project', 'project_name', 'goals')


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    metagoals = MetaGoalSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = ('id', 'url', 'name', 'metagoals')
