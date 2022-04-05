from django.contrib.auth.decorators import login_required
from django.db.models import F, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import models


@login_required
def create_to_do_list(request):
    try:
        to_do_list_title = request.POST["title"]
        if not to_do_list_title:
            raise KeyError
    except KeyError:
        return JsonResponse({
            "error": "You haven't provided a title for a to-do list!"
        })
    else:
        # noinspection PyUnresolvedReferences
        to_do_list = models.ToDoList.objects.create(
            title=to_do_list_title, owner=request.user,
        )
        return JsonResponse({
            "id": to_do_list.pk,
        })


@login_required
def get_to_do_lists(request):
    return JsonResponse([
        {"id": to_do_list.pk, "title": to_do_list.title}
        for to_do_list in request.user.todolist_set.all()
    ], safe=False)


def validate_do_to_list(function):
    def wrapper(request, to_do_list_id):
        to_do_list = get_object_or_404(models.ToDoList, pk=to_do_list_id)
        if request.user == to_do_list.owner:
            return function(request, to_do_list)
        else:
            return JsonResponse({
                "error": "This to-do list is not yours!"
            })
    return wrapper


def validate_task(function):
    def wrapper(request, task_id):
        task = get_object_or_404(models.Task, pk=task_id)
        if request.user == task.to_do_list.owner:
            return function(request, task)
        else:
            return JsonResponse({
                "error": "This to-do list is not yours!"
            })

    return wrapper


@login_required
@validate_do_to_list
def delete_to_do_list(_request, to_do_list):
    to_do_list.delete()
    return JsonResponse({})


@login_required
@validate_do_to_list
def get_tasks(_request, to_do_list):
    return JsonResponse([
        {
            "title": item.title, "is_done": item.is_done, "order": item.order,
            "id": item.pk,
        }
        for item in to_do_list.task_set.all()
    ], safe=False)


@login_required
@validate_task
def delete_task(_request, task):
    # noinspection PyUnresolvedReferences
    models.Task.objects.filter(
        to_do_list=task.to_do_list, order__gt=task.order
    ).update(order=F("order") - 1)
    task.delete()
    return JsonResponse({})


@login_required
def create_task(request):
    try:
        task_title = request.POST["title"]
        if not task_title:
            raise KeyError
    except KeyError:
        return JsonResponse({
            "error": "You haven't provided a title for a task!"
        })
    try:
        to_do_list_id = int(request.POST["to_do_list_id"])
    except (ValueError, KeyError):
        return JsonResponse({
            "error": (
                "You haven't provided an ID of a to-do list to which the task "
                "belongs!"
            )
        })
    to_do_list = get_object_or_404(models.ToDoList, pk=to_do_list_id)
    if to_do_list.owner != request.user:
        return JsonResponse({
            "error": "To-do list which you specified doesn't belong to you!"
        })
    # noinspection PyUnresolvedReferences
    try:
        # noinspection PyUnresolvedReferences
        max_task_order = models.Task.objects.filter(
            to_do_list=to_do_list,
        ).aggregate(Max("order"))["order__max"]
    except models.Task.DoesNotExist:
        max_task_order = 0
    # noinspection PyUnresolvedReferences
    task = models.Task.objects.create(
        title=task_title, order=(
            max_task_order + 1
        ), to_do_list=to_do_list,
    )
    return JsonResponse({
        "id": task.pk,
    })
