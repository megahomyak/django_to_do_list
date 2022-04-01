from django.urls import path

from . import views

app_name = "to_do_list"
urlpatterns = [
    path("create/", views.create_to_do_list, name="create"),
    path("view/<int:to_do_list_id>", views.view_to_do_list, name="view"),
]
