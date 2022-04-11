from django.urls import path

from . import views

app_name = "api"
urlpatterns = [
    path(
        "to_do_lists/create/", views.create_to_do_list,
        name="create_to_do_list",
    ),
    path(
        "to_do_lists/delete/", views.delete_to_do_list,
        name="delete_to_do_list",
    ),
    path(
        "to_do_lists/", views.get_to_do_lists, name="get_to_do_lists",
    ),
    path(
        "to_do_lists/<int:to_do_list_id>/", views.get_to_do_list_contents,
        name="get_to_do_list_contents",
    ),
    path("tasks/delete/", views.delete_task, name="delete_task"),
    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/reorder/", views.reorder_task, name="reorder_task"),
    path(
        "tasks/change_state/", views.change_task_state,
        name="change_task_state",
    ),
    path("tasks/rename/", views.rename_task, name="rename"),
    path("to_do_lists/rename/", views.rename_to_do_list, name="rename"),
]
