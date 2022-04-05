from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from api import models


@login_required
def view_to_do_list(request, to_do_list_id):
    to_do_list = get_object_or_404(models.ToDoList, pk=to_do_list_id)
    return render(
        request, (
            "frontend_app/accessible_to_do_list.html"
            if request.user == to_do_list.owner else
            "frontend_app/inaccessible_to_do_list.html"
        ), {
            "title": to_do_list.title,
            "to_do_list_id": to_do_list.pk,
            "creation_button_text": "Create new task",
        }
    )
