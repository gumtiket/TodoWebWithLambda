import json

import todos


def handler(event, context):
    route_key = event.get("routeKey")
    path_params = event.get("pathParameters") or {}

    try:
        if route_key == "GET /todos":
            query_params = event.get("queryStringParameters") or {}
            items = todos.list_todos(query_params.get("completed"))
            return _response(200, items)

        if route_key == "POST /todos":
            body = _parse_body(event.get("body"))
            item = todos.create_todo(body)
            return _response(201, item, extra_headers={"Location": f"/todos/{item['id']}"})

        if route_key == "GET /todos/{id}":
            item = todos.get_todo(path_params["id"])
            return _response(200, item) if item else _not_found()

        if route_key == "PATCH /todos/{id}":
            body = _parse_body(event.get("body"))
            item = todos.update_todo(path_params["id"], body)
            return _response(200, item) if item else _not_found()

        if route_key == "DELETE /todos/{id}":
            deleted = todos.delete_todo(path_params["id"])
            return _response(204, None) if deleted else _not_found()

        return _response(404, {"message": "route not found"})
    except ValueError as e:
        return _response(400, {"message": str(e)})


def _not_found():
    return _response(404, {"message": "todo not found"})


def _parse_body(raw_body):
    if not raw_body:
        return {}
    try:
        return json.loads(raw_body)
    except json.JSONDecodeError:
        raise ValueError("invalid JSON body")


def _response(status_code, body, extra_headers=None):
    headers = {"Content-Type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body) if body is not None else "",
    }
