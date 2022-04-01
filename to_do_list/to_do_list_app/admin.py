from django.contrib import admin

from to_do_list_app import models

admin.site.register((models.ToDoList, models.ToDoListItem))
