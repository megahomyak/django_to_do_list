import functools
import http

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from . import models

UNACCESSIBLE_TASK_ERROR_TEXT = "This task is not yours!"
UNACCESSIBLE_TO_DO_LIST_ERROR_TEXT = "This to-do list is not yours!"


def receiver_decorators_factory(checker, error_text, model_class):
    def post_field_setter(request_type, field_name):
        request_type = request_type.upper()

        def decorator(function):
            @functools.wraps(function)
            def wrapper(request, *args, **kwargs):
                if request_type == "GET":
                    database_entry_id = kwargs.pop(field_name)
                else:
                    [database_entry_id] = validate_post_integers(
                        request, field_name,
                    )
                object_ = get_object_or_404(
                    model_class, pk=database_entry_id
                )
                if checker(request, object_):
                    return function(request, object_, *args, **kwargs)
                else:
                    return JsonResponse(
                        {"error": error_text}, status=http.HTTPStatus.FORBIDDEN
                    )
            return wrapper
        return decorator
    return post_field_setter


receive_to_do_list = receiver_decorators_factory(
    error_text=UNACCESSIBLE_TO_DO_LIST_ERROR_TEXT, model_class=models.ToDoList,
    checker=lambda request, to_do_list: request.user == to_do_list.owner,
)
receive_task = receiver_decorators_factory(
    error_text=UNACCESSIBLE_TASK_ERROR_TEXT, model_class=models.Task,
    checker=lambda request, task: request.user == task.to_do_list.owner,
)


class JsonException(Exception):

    def __init__(self, error_body_in_json, status_code):
        self.error_body = error_body_in_json
        self.status_code = status_code


def with_json_exceptions(function):
    @functools.wraps(function)
    def wrapper(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except JsonException as error:
            return JsonResponse(
                {"error": error.error_body}, status=error.status_code
            )
    return wrapper


def with_json_exceptions_and_required_login(function):
    return login_required(with_json_exceptions(function))


def validate_post_integers(request, *field_names):
    integers = []
    for field_name in field_names:
        try:
            integers.append(int(request.POST[field_name]))
        except KeyError:
            raise JsonException(
                f"{field_name} is not specified!",
                http.HTTPStatus.BAD_REQUEST,
            ) from None
        except ValueError:
            raise JsonException(
                f"{field_name} is invalid!",
                http.HTTPStatus.BAD_REQUEST,
            ) from None
    return integers


def validate_post_strings(request, *field_names):
    strings = []
    for field_name in field_names:
        try:
            field_contents = request.POST[field_name]
        except KeyError:
            raise JsonException(
                f"{field_name} is not specified!",
                http.HTTPStatus.BAD_REQUEST,
            ) from None
        if not field_contents:
            raise JsonException(
                f"{field_name} is empty!",
                http.HTTPStatus.BAD_REQUEST,
            ) from None
        strings.append(field_contents)
    return strings
