import json
import os
from unittest.mock import patch

os.environ.setdefault("TODOS_TABLE_NAME", "todos-test")

import app


def test_list_todos_route():
    with patch("app.todos.list_todos", return_value=[{"id": "1"}]) as mock_list:
        event = {"routeKey": "GET /todos", "queryStringParameters": None}
        result = app.handler(event, None)

    assert result["statusCode"] == 200
    assert json.loads(result["body"]) == [{"id": "1"}]
    mock_list.assert_called_once_with(None)


def test_create_todo_route_returns_location_header():
    created = {"id": "abc", "title": "buy milk"}
    with patch("app.todos.create_todo", return_value=created):
        event = {"routeKey": "POST /todos", "body": json.dumps({"title": "buy milk"})}
        result = app.handler(event, None)

    assert result["statusCode"] == 201
    assert result["headers"]["Location"] == "/todos/abc"


def test_create_todo_route_invalid_json_returns_400():
    event = {"routeKey": "POST /todos", "body": "not-json"}
    result = app.handler(event, None)
    assert result["statusCode"] == 400


def test_create_todo_route_validation_error_returns_400():
    with patch("app.todos.create_todo", side_effect=ValueError("title is required")):
        event = {"routeKey": "POST /todos", "body": json.dumps({})}
        result = app.handler(event, None)

    assert result["statusCode"] == 400
    assert json.loads(result["body"])["message"] == "title is required"


def test_get_todo_route_not_found_returns_404():
    with patch("app.todos.get_todo", return_value=None):
        event = {"routeKey": "GET /todos/{id}", "pathParameters": {"id": "missing"}}
        result = app.handler(event, None)

    assert result["statusCode"] == 404


def test_delete_todo_route_returns_204():
    with patch("app.todos.delete_todo", return_value=True):
        event = {"routeKey": "DELETE /todos/{id}", "pathParameters": {"id": "abc"}}
        result = app.handler(event, None)

    assert result["statusCode"] == 204


def test_unknown_route_returns_404():
    event = {"routeKey": "GET /unknown"}
    result = app.handler(event, None)
    assert result["statusCode"] == 404
