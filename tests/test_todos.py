import importlib
import os

import boto3
import pytest
from moto import mock_aws

os.environ["TODOS_TABLE_NAME"] = "todos-test"


@pytest.fixture
def todos_module():
    with mock_aws():
        client = boto3.resource("dynamodb", region_name=os.environ["AWS_DEFAULT_REGION"])
        client.create_table(
            TableName="todos-test",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        import todos

        importlib.reload(todos)
        yield todos


def test_create_todo_sets_defaults(todos_module):
    item = todos_module.create_todo({"title": "buy milk"})
    assert item["title"] == "buy milk"
    assert item["completed"] is False
    assert item["createdAt"] == item["updatedAt"]


def test_create_todo_requires_title(todos_module):
    with pytest.raises(ValueError):
        todos_module.create_todo({"title": "  "})


def test_get_todo_returns_created_item(todos_module):
    created = todos_module.create_todo({"title": "buy milk"})
    fetched = todos_module.get_todo(created["id"])
    assert fetched == created


def test_get_todo_returns_none_when_missing(todos_module):
    assert todos_module.get_todo("does-not-exist") is None


def test_list_todos_filters_by_completed(todos_module):
    done = todos_module.create_todo({"title": "done task"})
    todos_module.update_todo(done["id"], {"completed": True})
    todos_module.create_todo({"title": "pending task"})

    completed_only = todos_module.list_todos("true")
    pending_only = todos_module.list_todos("false")

    assert [item["title"] for item in completed_only] == ["done task"]
    assert [item["title"] for item in pending_only] == ["pending task"]


def test_update_todo_returns_none_when_missing(todos_module):
    assert todos_module.update_todo("does-not-exist", {"completed": True}) is None


def test_update_todo_rejects_empty_title(todos_module):
    created = todos_module.create_todo({"title": "buy milk"})
    with pytest.raises(ValueError):
        todos_module.update_todo(created["id"], {"title": "  "})


def test_delete_todo_removes_item(todos_module):
    created = todos_module.create_todo({"title": "buy milk"})
    assert todos_module.delete_todo(created["id"]) is True
    assert todos_module.get_todo(created["id"]) is None


def test_delete_todo_returns_false_when_missing(todos_module):
    assert todos_module.delete_todo("does-not-exist") is False
