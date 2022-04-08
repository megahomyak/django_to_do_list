import http

from django.db import transaction
from django.db.models import F, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import models, view_utils
from .view_utils import (
    receive_to_do_list, receive_task, with_json_exceptions_and_required_login
)


@with_json_exceptions_and_required_login
def create_to_do_list(request):
    [to_do_list_title] = view_utils.validate_post_strings(request, "title")
    # noinspection PyUnresolvedReferences
    to_do_list = models.ToDoList.objects.create(
        title=to_do_list_title, owner=request.user,
    )
    return JsonResponse({
        "id": to_do_list.pk,
    })


@with_json_exceptions_and_required_login
def get_to_do_lists(request):
    return JsonResponse([
        {"id": to_do_list.pk, "title": to_do_list.title}
        for to_do_list in request.user.todolist_set.all()
    ], safe=False)


@with_json_exceptions_and_required_login
@receive_to_do_list("post", "to_do_list_id")
def delete_to_do_list(_request, to_do_list):
    to_do_list.delete()
    return JsonResponse({})


@with_json_exceptions_and_required_login
@receive_to_do_list("get", "to_do_list_id")
def get_to_do_list_contents(_request, to_do_list):
    return JsonResponse([
        {
            "title": item.title, "is_done": item.is_done, "order": item.order,
            "id": item.pk,
        }
        for item in to_do_list.task_set.all()
    ], safe=False)


@with_json_exceptions_and_required_login
@receive_task("post", "task_id")
def delete_task(_request, task):
    with transaction.atomic():
        # noinspection PyUnresolvedReferences
        models.Task.objects.filter(
            to_do_list=task.to_do_list, order__gt=task.order
        ).update(order=F("order") - 1)
        task.delete()
    return JsonResponse({})


@with_json_exceptions_and_required_login
def create_task(request):
    [task_title] = view_utils.validate_post_strings(request, "title")
    [to_do_list_id] = view_utils.validate_post_integers(
        request, "to_do_list_id"
    )
    to_do_list = get_object_or_404(models.ToDoList, pk=to_do_list_id)
    if to_do_list.owner != request.user:
        return JsonResponse({
            "error": "To-do list which you specified doesn't belong to you!",
        }, status=http.HTTPStatus.FORBIDDEN)
    with transaction.atomic():
        # noinspection PyUnresolvedReferences
        max_task_order = models.Task.objects.filter(
            to_do_list=to_do_list,
        ).aggregate(Max("order", default=0))["order__max"]
        # noinspection PyUnresolvedReferences
        task = models.Task.objects.create(
            title=task_title, order=(
                max_task_order + 1
            ), to_do_list=to_do_list,
        )
    return JsonResponse({
        "id": task.pk,
    })


@with_json_exceptions_and_required_login
def change_task_order(request):
    task_id, new_order = view_utils.validate_post_integers(
        request, "task_id", "new_order",
    )
    task = get_object_or_404(models.Task, pk=task_id)
    if task.to_do_list.owner != request.user:
        return JsonResponse({
            "error": (
                "Task which you specified doesn't belong to any of your to-do "
                "lists!"
            ),
        }, status=http.HTTPStatus.FORBIDDEN)
    old_order = task.order
    if old_order == new_order:
        return JsonResponse({})
    if old_order > new_order:
        # Example: if moving 5 (old_order) to 2 (new_order), move elements
        # between them (but not including the moved element, 5) up by 1
        bias = 1
        range_filters = {"order__gte": new_order, "order__lt": old_order}
    else:
        # Example: if moving 2 (old_order) to 5 (new_order), move elements
        # between them (but not including the moved element, 2) down by 1
        bias = -1
        range_filters = {"order__gt": old_order, "order__lte": new_order}
    with transaction.atomic():
        # noinspection PyUnresolvedReferences
        models.Task.objects.filter(
            to_do_list=task.to_do_list, **range_filters,
        ).update(order=F("order") + bias)
    return JsonResponse({})
