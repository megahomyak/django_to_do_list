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
        raise view_utils.JsonException(
            view_utils.UNACCESSIBLE_TO_DO_LIST_ERROR_TEXT,
            http.HTTPStatus.FORBIDDEN,
        )
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
def reorder_task(request):
    task_id, new_order = view_utils.validate_post_integers(
        request, "task_id", "new_order",
    )
    task = get_object_or_404(models.Task, pk=task_id)
    if task.to_do_list.owner != request.user:
        raise view_utils.JsonException(
            view_utils.UNACCESSIBLE_TASK_ERROR_TEXT,
            http.HTTPStatus.FORBIDDEN,
        )
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
    task.order = new_order
    task.save()
    return JsonResponse({})


@with_json_exceptions_and_required_login
def change_task_state(request):
    [task_id, new_state] = view_utils.validate_post_integers(
        request, "task_id", "new_state",
    )
    if new_state not in (0, 1):
        raise view_utils.JsonException(
            "new_state should be between 0 and 1!", http.HTTPStatus.BAD_REQUEST,
        )
    task = get_object_or_404(models.Task, pk=task_id)
    if task.to_do_list.owner != request.user:
        raise view_utils.JsonException(
            view_utils.UNACCESSIBLE_TASK_ERROR_TEXT,
            http.HTTPStatus.FORBIDDEN,
        )
    task.is_done = bool(new_state)
    task.save()
    return JsonResponse({})


def title_changers_generator(
    record_id_field_name, records_model, unaccessible_record_error_text,
    ownership_checker, function_name="rename_record"
):
    def rename_record(request):
        [record_id, new_title] = view_utils.validate_post_strings(
            request, record_id_field_name, "new_title",
        )
        try:
            record_id = int(record_id)
        except ValueError:
            raise view_utils.JsonException(
                "record_id is not an integer!", http.HTTPStatus.BAD_REQUEST,
            ) from None
        record = get_object_or_404(records_model, pk=record_id)
        if not ownership_checker(request, record):
            raise view_utils.JsonException(
                unaccessible_record_error_text, http.HTTPStatus.FORBIDDEN,
            )
        record.title = new_title
        record.save()
        return JsonResponse({})
    rename_record.__name__ = function_name
    return with_json_exceptions_and_required_login(rename_record)


rename_to_do_list = title_changers_generator(
    record_id_field_name="to_do_list_id", records_model=models.ToDoList,
    unaccessible_record_error_text=(
        view_utils.UNACCESSIBLE_TO_DO_LIST_ERROR_TEXT
    ), ownership_checker=lambda request, to_do_list: (
        request.user == to_do_list.owner
    ), function_name="rename_to_do_list"
)
rename_task = title_changers_generator(
    record_id_field_name="task_id", records_model=models.Task,
    unaccessible_record_error_text=(
        view_utils.UNACCESSIBLE_TASK_ERROR_TEXT
    ), ownership_checker=lambda request, task: (
        request.user == task.to_do_list.owner
    ), function_name="rename_task"
)
