import http

from django.contrib.auth.models import User

from . import models


def checkers_mixin_methods_generator(http_status):
    return lambda self, request: self.assertEqual(
        request.status_code, http_status
    )


class StatusCodeCheckersMixin:
    assertOk = checkers_mixin_methods_generator(http.HTTPStatus.OK)
    assertForbidden = checkers_mixin_methods_generator(
        http.HTTPStatus.FORBIDDEN
    )
    assertNotFound = checkers_mixin_methods_generator(
        http.HTTPStatus.NOT_FOUND
    )
    assertBadRequest = checkers_mixin_methods_generator(
        http.HTTPStatus.BAD_REQUEST
    )


class UsersFixture(StatusCodeCheckersMixin):

    # noinspection PyPep8Naming
    @classmethod
    def setUpTestData(cls):
        users = []
        for username in ("first", "second"):
            user = User.objects.create_user(username)
            users.append(user)
        cls.first_user, cls.second_user = users


class ToDoListsFixture(UsersFixture):

    # noinspection PyPep8Naming
    def setUp(self):
        # noinspection PyUnresolvedReferences
        # noinspection PyAttributeOutsideInit
        self.first_to_do_list, self.second_to_do_list = [
            models.ToDoList.objects.create(
                title=f"{owner_name}'s to-do list",
                owner=owner
            )
            for owner, owner_name in (
                (self.first_user, "First user"),
                (self.second_user, "Second user")
            )
        ]


class TasksFixture(ToDoListsFixture):

    def setUp(self):
        super().setUp()
        # noinspection PyUnresolvedReferences
        # noinspection PyAttributeOutsideInit
        self.first_task, self.second_task = [
            models.Task.objects.create(
                title=f"A task that belongs to \"{to_do_list.title}\"",
                order=1,
                to_do_list=to_do_list
            )
            for to_do_list in (self.first_to_do_list, self.second_to_do_list)
        ]
