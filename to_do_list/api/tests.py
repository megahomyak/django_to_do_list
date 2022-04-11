from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from . import models
from .test_utils import ToDoListsFixture, TasksFixture, StatusCodeCheckersMixin


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


class TaskReorderingTests(StatusCodeCheckersMixin, TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_with_five_tasks = User.objects.create_user(
            "user with five tasks"
        )
        # noinspection PyUnresolvedReferences
        cls.to_do_list_with_five_tasks = models.ToDoList.objects.create(
            owner=cls.user_with_five_tasks,
            title="to-do list with five tasks"
        )

    def setUp(self):
        self.tasks = {}
        for task_number, task_name in enumerate(
            ("first", "second", "third", "fourth", "fifth"), start=1,
        ):
            # noinspection PyUnresolvedReferences
            self.tasks[task_name] = models.Task.objects.create(
                title=task_name, order=task_number,
                to_do_list=self.to_do_list_with_five_tasks
            )
        self.client.force_login(self.user_with_five_tasks)

    def assertTitlesAreEqual(self, response, titles):
        self.assertEqual(
            [task["title"] for task in response.json()],
            titles,
        )

    def reorder(self, task_id, new_order):
        return self.client.post(reverse("api:reorder_task"), {
            "task_id": task_id,
            "new_order": new_order,
        })

    def reorder_and_compare(self, task_title, new_order, new_titles):
        response = self.reorder(self.tasks[task_title].pk, new_order)
        self.assertOk(response)
        response = self.client.get(reverse(
            "api:get_to_do_list_contents",
            args=(self.to_do_list_with_five_tasks.pk,),
        ))
        self.assertOk(response)
        self.assertTitlesAreEqual(response, new_titles)

    def test_bigger_to_smaller_reordering(self):
        self.reorder_and_compare(
            "fourth", 2, ["fifth", "third", "second", "fourth", "first"],
        )

    def test_smaller_to_bigger_reordering(self):
        self.reorder_and_compare(
            "second", 4, ["fifth", "second", "fourth", "third", "first"],
        )

    def test_nonexistent_task_reordering(self):
        response = self.reorder(task_id=-1, new_order=0)
        self.assertNotFound(response)

    def test_inaccessible_task_reordering(self):
        # noinspection PyUnresolvedReferences
        inaccessible_task = models.Task.objects.create(
            title="inaccessible task", order=0,
            to_do_list=models.ToDoList.objects.create(
                title="inaccessible to-do list",
                owner=User.objects.create_user("owner of inaccessible objects")
            )
        )
        response = self.reorder(inaccessible_task.pk, 0)
        self.assertForbidden(response)

    def test_too_small_order_reordering(self):
        self.reorder_and_compare(
            "fifth", -123, ["fourth", "third", "second", "first", "fifth"],
        )

    def test_very_big_order_reordering(self):
        self.reorder_and_compare(
            "first", 999, ["first", "fifth", "fourth", "third", "second"],
        )


class TaskStateChangingTests(TasksFixture, TestCase):

    def setUp(self):
        TasksFixture.setUp(self)
        self.client.force_login(self.first_user)

    def test_changing_state_of_an_inaccessible_task(self):
        response = self.client.post(reverse("api:change_task_state"), {
            "new_state": 0,
            "task_id": self.second_task.pk,
        })
        self.assertForbidden(response)

    def test_changing_task_state_to_an_invalid_bigger_value(self):
        response = self.client.post(reverse("api:change_task_state"), {
            "new_state": 2,
            "task_id": self.first_task,
        })
        self.assertBadRequest(response)

    def test_changing_task_state_to_an_invalid_smaller_value(self):
        response = self.client.post(reverse("api:change_task_state"), {
            "new_state": -1,
            "task_id": self.first_task,
        })
        self.assertBadRequest(response)

    def test_changing_accessible_task_state(self):

        def assert_is_done_equal_to(expected_is_done_state):
            response = self.client.get(reverse(
                "api:get_to_do_list_contents", args=(self.first_to_do_list.pk,)
            ))
            self.assertOk(response)
            self.assertEqual(
                response.json()[0]["is_done"], expected_is_done_state
            )

        def change_task_state(new_task_state):
            response = self.client.post(reverse("api:change_task_state"), {
                "new_state": new_task_state,
                "task_id": self.first_task.pk,
            })
            self.assertOk(response)

        assert_is_done_equal_to(False)
        change_task_state(1)
        assert_is_done_equal_to(True)
        change_task_state(0)
        assert_is_done_equal_to(False)


class TaskTitleChangingTests(TasksFixture, TestCase):

    def setUp(self):
        TasksFixture.setUp(self)
        self.client.force_login(self.first_user)

    def rename_task(self, new_title, task_id=None):
        response = self.client.post(reverse("api:rename_task"), {
            "task_id": self.first_task.pk if task_id is None else task_id,
            "new_title": new_title,
        })
        return response

    def test_empty_task_title(self):
        response = self.rename_task("")
        self.assertBadRequest(response)

    def test_missing_task_title(self):
        response = self.client.post(reverse("api:rename_task"), {
            "task_id": self.first_task.pk,
        })
        self.assertBadRequest(response)

    def test_inaccessible_task_renaming(self):
        response = self.rename_task(
            new_title="abc", task_id=self.second_task.pk
        )
        self.assertForbidden(response)

    def test_accessible_task_renaming(self):
        response = self.rename_task(new_title="new task name after renaming")
        self.assertOk(response)
        response = self.client.get(reverse(
            "api:get_to_do_list_contents", args=(self.first_to_do_list.pk,)
        ))
        self.assertIn("new task name after renaming", (
            record["title"] for record in response.json()
        ))
