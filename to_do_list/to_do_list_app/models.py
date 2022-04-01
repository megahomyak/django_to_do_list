from django.contrib.auth.models import User
from django.db import models


class ToDoList(models.Model):
    title = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class ToDoListItem(models.Model):
    title = models.TextField()
    is_done = models.BooleanField()
    to_do_list = models.ForeignKey(ToDoList, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
