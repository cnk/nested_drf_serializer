from django.contrib import admin
from .models import Project, MetaGoal, Goal

# Register your models here.
admin.site.register(Project)
admin.site.register(MetaGoal)
admin.site.register(Goal)

