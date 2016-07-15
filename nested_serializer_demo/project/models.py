from django.db import models

class Project(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)

    def __str__(self):
        return self.name


class MetaGoal(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    project = models.ForeignKey('Project', related_name='metagoals', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class MetaGoalPrerequisite(models.Model):
    """
    Some metagoals require completion of other metagoals;
    This table provides the mappings between parent metagoals and their children.
    """

    parent = models.ForeignKey('MetaGoal', db_column='parent_key', related_name='mg_dependants', on_delete=models.CASCADE)
    child = models.ForeignKey('MetaGoal', db_column='child_key', related_name='mg_prerequisites', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return "{0} depends on {1}".format(self.child, self.parent)

    # returns 1 if node's dependent tree reaches top_node
    # using Depth-first search traversal
    @staticmethod
    def check_for_loop(next_node, top_node, visited_nodes):
        top_key = top_node.metagoal_key
        children = MetaGoalPrerequisite.objects.filter(parent=next_node.metagoal_key)
        for node_key in children:
            # print(node_key.child)
            node = MetaGoal.objects.filter(metagoal_key=node_key.child)[0]
            if node not in visited_nodes:
                # print("!!compare ", node.goal_key, top_key)
                if node.metagoal_key == top_key:
                    return 1
                else:
                    visited_nodes.append(node)
                    if MetaGoalPrerequisite.check_for_loop(node, top_node, visited_nodes):
                        return 1
        return 0

    def clean(self):
        # don't let goals depend on themselves
        if self.parent == self.child:
            raise ValidationError("A metagoal can not depend on itself.")

        # All course attributes must match
        if not self.parent.course_id == self.child.course_id:
            raise ValidationError("Both metagoals must belong to this record's course.")

        # don't allow the new prerequisite create any loop
        # make sure self.child's dependent tree not to reach self.parent
        visited_nodes = []
        if self.check_for_loop(self.child, self.parent, visited_nodes):
            raise ValidationError("A loop occurred in current dependence graph.")

class Goal(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256, unique=True)
    metagoal = models.ForeignKey('MetaGoal', related_name='goals', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class GoalPrerequisite(models.Model):
    """
    Some goals require completion of other goals;
    This table provides the mappings between parent goals and their children.
    """

    parent = models.ForeignKey('Goal', db_column='parent_key', related_name='dependants', on_delete=models.CASCADE)
    child = models.ForeignKey('Goal', db_column='child_key', related_name='prerequisites', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('parent', 'child')

    def __str__(self):
        return "{0} depends on {1}".format(self.child, self.parent)

    # returns 1 if node's dependent tree reaches top_node
    # using Depth-first search traversal
    @staticmethod
    def check_for_loop(next_node, top_node, visited_nodes):
        top_key = top_node.metagoal_key
        children = MetaGoalPrerequisite.objects.filter(parent=next_node.metagoal_key)
        for node_key in children:
            # print(node_key.child)
            node = MetaGoal.objects.filter(metagoal_key=node_key.child)[0]
            if node not in visited_nodes:
                # print("!!compare ", node.goal_key, top_key)
                if node.metagoal_key == top_key:
                    return 1
                else:
                    visited_nodes.append(node)
                    if MetaGoalPrerequisite.check_for_loop(node, top_node, visited_nodes):
                        return 1
        return 0

    def clean(self):
        # don't let goals depend on themselves
        if self.parent == self.child:
            raise ValidationError("A metagoal can not depend on itself.")

        # All course attributes must match
        if not self.parent.course_id == self.child.course_id:
            raise ValidationError("Both metagoals must belong to this record's course.")

        # don't allow the new prerequisite create any loop
        # make sure self.child's dependent tree not to reach self.parent
        visited_nodes = []
        if self.check_for_loop(self.child, self.parent, visited_nodes):
            raise ValidationError("A loop occurred in current dependence graph.")
