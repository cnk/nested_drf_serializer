"""nested_serializer_demo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework import routers
from nested_serializer_demo.project.views import ProjectViewSet, MetaGoalViewSet, MetaGoalPrerequisiteViewSet, \
    GoalViewSet, GoalPrerequisiteViewSet


router = routers.DefaultRouter()
router.register(r'projects', ProjectViewSet)
router.register(r'metagoals', MetaGoalViewSet)
router.register(r'metagoal_prerequisites', MetaGoalPrerequisiteViewSet)
router.register(r'goals', GoalViewSet)
router.register(r'goal_prerequisites', GoalPrerequisiteViewSet)


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^admin/', include(admin.site.urls)),
]
