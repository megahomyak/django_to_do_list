from django.urls import path

from . import views

app_name = "to_do_list"
urlpatterns = [
    path("<int:to_do_list_id>", views.view_to_do_list, name="view"),
]
