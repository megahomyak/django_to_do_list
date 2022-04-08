from django.contrib import admin

from . import models


def make_model_admin_with_id(primary_key_column_name, model):
    # noinspection PyProtectedMember
    return type(
        model.__name__, (admin.ModelAdmin,),
        {"readonly_fields": (primary_key_column_name,)}
    )


def register_with_id(primary_key_column_name, *models_):
    for model in models_:
        admin.site.register(model, make_model_admin_with_id(
            primary_key_column_name, model
        ))


register_with_id("id", models.Task, models.ToDoList)
