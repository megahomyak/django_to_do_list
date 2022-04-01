from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from . import models


@login_required
def create_to_do_list(request):
    try:
        to_do_list_title = request.POST["title"]
        if not to_do_list_title:
            raise KeyError
    except KeyError:
        return render(request, "to_do_list_app/index.html", {
            "error_message": "You haven't provided a title for a to-do list!"
        })
    else:
        # noinspection PyUnresolvedReferences
        models.ToDoList.objects.create(
            title=to_do_list_title, owner=request.user,
        )
        return redirect("index")


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
