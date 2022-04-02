import http

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404

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
def view_to_do_list(request, to_do_list_id):
    to_do_list = get_object_or_404(models.ToDoList, pk=to_do_list_id)
    return render(
        request, (
            "to_do_list_app/accessible_to_do_list.html"
            if request.user == to_do_list.owner else
            "to_do_list_app/inaccessible_to_do_list.html"
        )
    )


@login_required
def get_to_do_lists(request):
    return JsonResponse([
        {"id": to_do_list.pk, "title": to_do_list.title}
        for to_do_list in request.user.todolist_set.all()
    ], safe=False)


@login_required
def delete_to_do_list(request, to_do_list_id):
    to_do_list = get_object_or_404(models.ToDoList, to_do_list_id)
    if request.user == to_do_list.owner:
        to_do_list.delete()
        return HttpResponse(
            "a", status=http.HTTPStatus.NO_CONTENT, content_type="text/plain"
        )  # And also tried that - none of them work as intended,
        # all of them return 200 with <html><head></head><body></body></html>
        # in their body. IDK WTF
    else:
        return JsonResponse({
            "error": "This to-do list is not yours!"
        })
