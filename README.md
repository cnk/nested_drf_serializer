This project exists to explore query tuning while building Django Rest
Framework APIs. It uses Django 1.8 (specifically I used 1.8.13) and
Django Rest Framework version 3.4.0.

## To use this example ##

1. Set up a python virtualenv using whatever tools you
   prefer. Personally I can't live without [pyenv-virtualenv[(https://github.com/yyuu/pyenv-virtualenv)


2. Install the required software:
           `pip install -r requirements.text`

3. Run the migrations:
           `./manage.py migrate`
   The current settings file will create a sqlite3 database in the top
   level directory of this project.

4. Start the dev server so you can watch the queries being logged to
   the console:
           `./manage.py runserver`



# Observations #

## Serializers with nested children ##

The most basic representation of this set of nested models is for each
model to include a serialization of the model below it. So for this
example, the ProjectSerializer includes the metagoals for each project:

    class ProjectSerializer(serializers.HyperlinkedModelSerializer):
        metagoals = MetaGoalSerializer(many=True, read_only=True)

        class Meta:
            model = Project
            fields = ('id', 'url', 'name', 'metagoals')

    class MetaGoalSerializer(serializers.HyperlinkedModelSerializer):
        goals = GoalSerializer(many=True, read_only=True)

        class Meta:
            model = MetaGoal
            fields = ('id', 'url', 'name', 'project', 'goals')

    class GoalSerializer(serializers.HyperlinkedModelSerializer):
        class Meta:
            model = Goal
            fields = ('id', 'url', 'name', 'metagoal')

With a default ModelSerializer and ModelViewSet for each model and the
most basic of queryset definitions, e.g. `queryset = Project.objects.all()`,
the number of queries done for the project list view increases by 1 each
time you add a new project or a new metagoal (but not when you add new
goals, aka when adding a leaf to the tree).

If you change the queryset argument for the ProjectSerializer to
prefetch all the related metagoals and goals you can reduce the number
of queries to 3 - and this number remains constant no matter how many
new projects or metagoals are added. So this is a general rule: add
the relation name for each of your nested serializers to the
`prefetch_related` part of your queryset definition.

    class ProjectViewSet(viewsets.ModelViewSet):
        queryset = Project.objects.prefetch_related('metagoals', 'metagoals__goals').all()
        serializer_class = ProjectSerializer

    curl http://127.0.0.1:8000/api/projects/ | jq .

    Console:

    (0.000) QUERY = 'SELECT "project_project"."id", "project_project"."name" FROM "project_project"' - PARAMS = (); args=()

    (0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."project_id" IN (%s, %s, %s)' - PARAMS = (1, 2, 3); args=(1, 2, 3)

    (0.000) QUERY = 'SELECT "project_goal"."id", "project_goal"."name", "project_goal"."metagoal_id" FROM "project_goal" WHERE "project_goal"."metagoal_id" IN (%s, %s, %s)' - PARAMS = (1, 2, 3); args=(1, 2, 3, 4, 5)

    [SQL] 3 queries (0 duplicates), 0 ms SQL time, 28 ms total request time
    [15/Jul/2016 01:34:42] "GET /api/projects/ HTTP/1.1" 200 13432


## Serializers with data from parent objects ##

For my real project, I often want data from the parent object in
objects. For example, when displaying a metagoal, I often want to show
the name of the project it belongs to. So, to make things easy in my
JavaScript layer, I want project_name included in each metagoal.

    class MetaGoalSerializer(serializers.HyperlinkedModelSerializer):
        goals = GoalSerializer(many=True, read_only=True)
        project_name = serializers.CharField(source='project.name')

        class Meta:
                model = MetaGoal
                fields = ('id', 'url', 'name', 'project', 'project_name', 'goals')

Interestingly, adding project_name to this serializer doesn't change
how many queries are done for the `/projects/` endpoint - it still takes
the same 3 queries. But to get the `/metagoals/` endpoint, now takes
`(2 + n)` queries - where `n` is the number of metagoals you have. To fix
this, we add `.select_related('project')` to the MetaGoalViewSet
queryset parameter and that brings us back down to a constant 2 queries.


    class MetaGoalViewSet(viewsets.ModelViewSet):
        queryset = MetaGoal.objects.select_related('project').prefetch_related('goals').all()
        serializer_class = MetaGoalSerializer


## Oddities ##

Prerequisite table does 7 queries, even when it doesn't display any of
the queried data:

class MetaGoalPrerequisiteViewSet(viewsets.ModelViewSet):
    queryset = MetaGoalPrerequisite.objects.all()
    serializer_class = MetaGoalPrerequisiteSerializer

class MetaGoalPrerequisiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MetaGoalPrerequisite
        fields = ('id', 'url')

]$ curl http://127.0.0.1:8000/metagoal_prerequisites/ | jq .
[
  {
    "id": 1,
    "url": "http://127.0.0.1:8000/metagoal_prerequisites/1/"
  },
  {
    "id": 2,
    "url": "http://127.0.0.1:8000/metagoal_prerequisites/2/"
  },
  {
    "id": 3,
    "url": "http://127.0.0.1:8000/metagoal_prerequisites/3/"
  }
]

(0.000) QUERY = 'SELECT "project_metagoalprerequisite"."id", "project_metagoalprerequisite"."parent_key", "project_metagoalprerequisite"."child_key" FROM "project_metagoalprerequisite"' - PARAMS = (); args=()
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (2,); args=(2,)
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (1,); args=(1,)
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (3,); args=(3,)
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (2,); args=(2,)
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (3,); args=(3,)
(0.000) QUERY = 'SELECT "project_metagoal"."id", "project_metagoal"."name", "project_metagoal"."project_id" FROM "project_metagoal" WHERE "project_metagoal"."id" = %s' - PARAMS = (1,); args=(1,)
[SQL] 7 queries (3 duplicates), 0 ms SQL time, 58 ms total request time
[15/Jul/2016 22:16:59] "GET /metagoal_prerequisites/ HTTP/1.1" 200 196

Changing the queryset to `MetaGoalPrerequisite.objects.select_related('parent', 'child').all()`
fixes it. But I don't understand why I had the problem in the first
place:

(0.000) QUERY = 'SELECT "project_metagoalprerequisite"."id",
        "project_metagoalprerequisite"."parent_key",
        "project_metagoalprerequisite"."child_key", "project_metagoal"."id",
        "project_metagoal"."name",
        "project_metagoal"."project_id", T3."id", T3."name", T3."project_id"
FROM "project_metagoalprerequisite" INNER JOIN "project_metagoal"
  ON ("project_metagoalprerequisite"."parent_key" = "project_metagoal"."id")
INNER JOIN "project_metagoal" T3
  ON ("project_metagoalprerequisite"."child_key" = T3."id" )' - PARAMS = ();
args=()

[SQL] 1 queries (0 duplicates), 0 ms SQL time, 84 ms total request time
[15/Jul/2016 22:22:36] "GET /metagoal_prerequisites/ HTTP/1.1" 200 196
