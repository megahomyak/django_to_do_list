from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path("to_do_lists/create/", views.create_to_do_list),
    path("to_do_lists/<int:to_do_list_id>/delete/", views.delete_to_do_list),
    path("to_do_lists/", views.get_to_do_lists),
    path("to_do_lists/<int:to_do_list_id>", views.get_tasks),
    path("tasks/<int:task_id>/delete", views.delete_task),
    path("tasks/create", views.create_task),
]
