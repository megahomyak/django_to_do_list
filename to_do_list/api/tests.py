from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .test_utils import ToDoListsFixture, TasksFixture


class ToDoListDeletionTests(ToDoListsFixture, TestCase):

    def test_deletion_of_an_inaccessible_to_do_list(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_to_do_list"), {
            "to_do_list_id": self.second_to_do_list.pk
        })
        self.assertForbidden(response)

    def test_deletion_of_an_accessible_to_do_list(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_to_do_list"), {
            "to_do_list_id": self.first_to_do_list.pk
        })
        self.assertOk(response)
        response = self.client.get(reverse("api:get_to_do_lists"))
        self.assertEqual(response.json(), [])

    def test_deletion_of_nonexistent_to_do_list(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_to_do_list"), {
            "to_do_list_id": -1
        })
        self.assertNotFound(response)

    def test_deletion_when_user_is_deleted(self):
        new_user = User.objects.create_user("new user")
        self.client.force_login(new_user)
        response = self.client.post(reverse("api:create_to_do_list"), {
            "title": "ABC",
        })
        self.assertOk(response)
        new_list_id = response.json()["id"]

        def get_to_do_list():
            return self.client.get(reverse(
                "api:get_to_do_list_contents", args=(new_list_id,)
            ))
        response = get_to_do_list()
        self.assertOk(response)

        self.client.force_login(self.first_user)
        response = get_to_do_list()
        self.assertForbidden(response)
        new_user.delete()
        response = get_to_do_list()
        self.assertNotFound(response)


class ToDoListCreationTests(ToDoListsFixture, TestCase):

    def test_list_creation(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:create_to_do_list"), {
            "title": "ABC",
        })
        self.assertIn("id", response.json())
        self.assertOk(response)
        response = self.client.get(reverse("api:get_to_do_lists"))
        self.assertIn("ABC", (row["title"] for row in response.json()))

    def test_untitled_list_creation_failure(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:create_to_do_list"))
        self.assertBadRequest(response)
        response = self.client.post(reverse("api:create_to_do_list"), {
            "title": "",
        })
        self.assertBadRequest(response)


class TaskDeletionTests(TasksFixture, TestCase):

    def test_deletion_of_an_inaccessible_task(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_task"), {
            "task_id": self.second_task.pk
        })
        self.assertForbidden(response)

    def test_deletion_of_an_accessible_task(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_task"), {
            "task_id": self.first_task.pk
        })
        self.assertOk(response)
        response = self.client.get(reverse(
            "api:get_to_do_list_contents", args=(self.first_to_do_list.pk,)
        ))
        self.assertEqual(response.json(), [])

    def test_deletion_of_nonexistent_task(self):
        self.client.force_login(self.first_user)
        response = self.client.post(reverse("api:delete_to_do_list"), {
            "to_do_list_id": -1
        })
        self.assertNotFound(response)

    def test_deletion_when_user_is_deleted(self):
        new_user = User.objects.create_user("new user")
        self.client.force_login(new_user)
        response = self.client.post(reverse("api:create_to_do_list"), {
            "title": "ABC",
        })
        self.assertOk(response)
        new_to_do_list_id = response.json()["id"]
        response = self.client.post(reverse("api:create_task"), {
            "title": "DEF",
            "to_do_list_id": new_to_do_list_id,
        })
        new_task_id = response.json()["id"]

        def get_tasks():
            return self.client.get(reverse(
                "api:get_to_do_list_contents", args=(new_to_do_list_id,)
            ))

        def get_to_do_lists():
            return self.client.get(reverse("api:get_to_do_lists"))

        def delete_task():
            return self.client.post(reverse("api:delete_task"), {
                "task_id": new_task_id,
            })
        response = get_to_do_lists()
        self.assertOk(response)
        self.assertIn("ABC", (
            to_do_list["title"] for to_do_list in response.json()
        ))
        response = get_tasks()
        self.assertOk(response)
        self.assertIn("DEF", (
            task["title"] for task in response.json()
        ))

        self.client.force_login(self.first_user)
        response = get_tasks()
        self.assertForbidden(response)
        response = delete_task()
        self.assertForbidden(response)
        new_user.delete()
        response = get_tasks()
        self.assertNotFound(response)
        response = delete_task()
        self.assertNotFound(response)
