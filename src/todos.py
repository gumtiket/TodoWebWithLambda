import os
import uuid
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr

_dynamodb = boto3.resource("dynamodb")
_table = _dynamodb.Table(os.environ["TODOS_TABLE_NAME"])


def list_todos(completed_filter=None):
    scan_kwargs = {}
    if completed_filter is not None:
        scan_kwargs["FilterExpression"] = Attr("completed").eq(completed_filter.lower() == "true")
    items = _table.scan(**scan_kwargs).get("Items", [])
    return sorted(items, key=lambda item: item["createdAt"])


def create_todo(body):
    title = (body or {}).get("title", "").strip()
    if not title:
        raise ValueError("title is required")
    now = _now()
    item = {
        "id": str(uuid.uuid4()),
        "title": title,
        "completed": False,
        "createdAt": now,
        "updatedAt": now,
    }
    _table.put_item(Item=item)
    return item


def get_todo(todo_id):
    return _table.get_item(Key={"id": todo_id}).get("Item")


def update_todo(todo_id, body):
    existing = get_todo(todo_id)
    if existing is None:
        return None
    if "title" in body:
        title = body["title"].strip()
        if not title:
            raise ValueError("title must not be empty")
        existing["title"] = title
    if "completed" in body:
        existing["completed"] = bool(body["completed"])
    existing["updatedAt"] = _now()
    _table.put_item(Item=existing)
    return existing


def delete_todo(todo_id):
    existing = get_todo(todo_id)
    if existing is None:
        return False
    _table.delete_item(Key={"id": todo_id})
    return True


def _now():
    return datetime.now(timezone.utc).isoformat()
