from rest_framework import viewsets
from .models import Project, MetaGoal, MetaGoalPrerequisite, Goal, GoalPrerequisite
from .serializers import ProjectSerializer, MetaGoalSerializer, MetaGoalPrerequisiteSerializer, \
    GoalSerializer, GoalPrerequisiteSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.prefetch_related('metagoals', 'metagoals__goals').all()
    serializer_class = ProjectSerializer


class MetaGoalViewSet(viewsets.ModelViewSet):
    queryset = MetaGoal.objects.select_related('project').prefetch_related('goals').all()
    serializer_class = MetaGoalSerializer


class MetaGoalPrerequisiteViewSet(viewsets.ModelViewSet):
    # queryset = MetaGoalPrerequisite.objects.select_related('parent', 'child').all()
    queryset = MetaGoalPrerequisite.objects.all()
    serializer_class = MetaGoalPrerequisiteSerializer


class GoalViewSet(viewsets.ModelViewSet):
    queryset = Goal.objects.select_related('metagoal').all()
    serializer_class = GoalSerializer


class GoalPrerequisiteViewSet(viewsets.ModelViewSet):
    queryset = GoalPrerequisite.objects.select_related('parent', 'child').all()
    serializer_class = GoalPrerequisiteSerializer

