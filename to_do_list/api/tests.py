from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .test_utils import ToDoListsFixture, TasksFixture, GenericTestsMixin


# =====================================
# WARNING FOR ANYONE WHO WILL READ THIS
# When writing this file, I concluded that unittest (library) is bad (because
# it supports a little amount of useful testing tools, providing only basic
# functionality, and, for example, sharing some logic with some abstractions
# between tests (and then implementing these abstract bits in concrete tests)
# is not an easy task).
# In my future projects, I will use pytest.
# So if you find some bad code here, know that with pytest I would have written
# it better.
# =====================================
# Later thoughts:
# These tests are the worst I've ever written
# Even later thoughts:
# These tests are bad even in terms of unittest


class GenericDeletionTests(GenericTestsMixin):

    @classmethod
    def set_up(
        cls, deletion_url, entry_id_field_name,
        all_records_getter_url, single_record_getter_view_name,
        creation_url, creation_request_parameters,
    ):
        cls.deletion_url = deletion_url
        cls.entry_id_field_name = entry_id_field_name
        cls.all_records_getter_url = all_records_getter_url
        cls.single_record_getter_view_name = single_record_getter_view_name
        cls.creation_url = creation_url
        cls.creation_request_parameters = creation_request_parameters
        cls.first_owned_record_primary_key = None
        cls.second_owned_record_primary_key = None

    def delete_record_by_primary_key(self, owned_record_primary_key):
        return self.client.post(self.deletion_url, {
            self.entry_id_field_name: owned_record_primary_key
        })

    def get_all_records(self):
        return self.client.get(self.all_records_getter_url)

    def test_deletion_of_an_inaccessible_record(self):
        self.client.force_login(self.first_user)
        response = self.delete_record_by_primary_key(
            self.second_owned_record_primary_key
        )
        self.assertForbidden(response)

    def test_deletion_of_an_accessible_record(self):
        self.client.force_login(self.first_user)
        response = self.delete_record_by_primary_key(
            self.first_owned_record_primary_key
        )
        self.assertOk(response)
        response = self.get_all_records()
        # noinspection PyUnresolvedReferences
        self.assertEqual(response.json(), [])

    def test_deletion_of_nonexistent_record(self):
        self.client.force_login(self.first_user)
        response = self.delete_record_by_primary_key(-1)
        self.assertNotFound(response)

    def test_deletion_when_user_is_deleted(self):
        new_user = User.objects.create_user("new user")
        self.client.force_login(new_user)
        response = self.client.post(
            self.creation_url, self.creation_request_parameters,
        )
        self.assertOk(response)
        new_list_id = response.json()["id"]

        def get_last_record():
            return self.client.get(reverse(
                self.single_record_getter_view_name, args=(new_list_id,)
            ))
        response = get_last_record()
        self.assertOk(response)

        self.client.force_login(self.first_user)
        response = get_last_record()
        self.assertForbidden(response)
        new_user.delete()
        response = get_last_record()
        self.assertNotFound(response)


class GenericCreationTests(GenericTestsMixin):

    @classmethod
    def set_up(
        cls, creation_url, creation_request_parameters,
        creation_response_items_checker, invalid_creation_request_parameters,
        getter_url,
    ):
        cls.creation_url = creation_url
        cls.creation_request_parameters = creation_request_parameters
        cls.getter_url = getter_url
        cls.creation_response_items_checker = (
            creation_response_items_checker
        )
        cls.invalid_creation_request_parameters = (
            invalid_creation_request_parameters
        )

    def test_record_creation(self):
        self.client.force_login(self.first_user)
        response = self.client.post(
            self.creation_url, self.creation_request_parameters,
        )
        # noinspection PyUnresolvedReferences
        self.assertIn("id", response.json())
        self.assertOk(response)
        response = self.client.get(self.getter_url)
        # noinspection PyUnresolvedReferences
        self.assertTrue(any(
            self.creation_response_items_checker(to_do_list)
            for to_do_list in response.json()
        ))

    def test_untitled_record_creation_failure(self):
        self.client.force_login(self.first_user)
        response = self.client.post(self.creation_url)
        self.assertBadRequest(response)
        response = self.client.post(
            self.creation_url, self.invalid_creation_request_parameters
        )
        self.assertBadRequest(response)


class ToDoListCreationTests(GenericCreationTests, TestCase):

    @classmethod
    def setUpTestData(cls):
        GenericCreationTests.set_up(
            creation_url=reverse("api:create_to_do_list"),
            creation_request_parameters={"title": "ABC"},
            creation_response_items_checker=lambda to_do_list: (
                to_do_list["title"] == "ABC"
            ),
            invalid_creation_request_parameters={"title": ""},
            getter_url=reverse("api:get_to_do_lists"),
        )


class TaskCreationTests(GenericCreationTests, TestCase):

    @classmethod
    def setUpTestData(cls):
        GenericCreationTests.set_up(
            creation_url=reverse("api:create_task"),
            creation_request_parameters_getter={"title": "ABC", "to_do_list"},
            creation_response_items_checker=lambda to_do_list: (
                to_do_list["title"] == "ABC"
            ),
            invalid_creation_request_parameters={"title": ""},
            getter_url=reverse("api:get_to_do_lists"),
        )


class ToDoListDeletionTests(TestCase, GenericDeletionTests, ToDoListsFixture):

    @classmethod
    def setUpTestData(cls):
        ToDoListsFixture.setUpTestData()
        GenericDeletionTests.set_up(
            deletion_url=reverse("api:delete_to_do_list"),
            entry_id_field_name="to_do_list_id",
            all_records_getter_url=reverse("api:get_to_do_lists"),
            single_record_getter_view_name="api:get_to_do_list_contents",
            creation_url=reverse("api:create_to_do_list"),
            creation_request_parameters={"title": "ABC"}
        )

    def setUp(self):
        ToDoListsFixture.setUp(self)
        self.first_owned_record_primary_key = self.first_to_do_list.pk
        self.second_owned_record_primary_key = self.second_to_do_list.pk


class TaskDeletionTests(TestCase, GenericDeletionTests, TasksFixture):

    @classmethod
    def setUpTestData(cls):
        TasksFixture.setUpTestData()
        GenericDeletionTests.set_up(
            deletion_url=reverse("api:delete_task"),
            entry_id_field_name="task_id",
            all_records_getter_url=None,
            single_record_getter_view_name=None,
            creation_url=None,
            creation_request_parameters=None,
        )

    def setUp(self):
        TasksFixture.setUp(self)
        self.first_owned_record_primary_key = self.first_to_do_list.pk
        self.second_owned_record_primary_key = self.second_to_do_list.pk

    def get_all_records(self):
        return self.client.get(reverse(
            "api:get_to_do_list_contents", args=(self.first_to_do_list.pk,)
        ))

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
