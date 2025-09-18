import boto3
import os
from datetime import datetime

# DynamoDB client
dynamodb = boto3.client("dynamodb", region_name="ap-south-1")

# Tables (set via env vars or fallback defaults)
COURSE_TABLE = os.environ.get("COURSE_TABLE", "CourseTracking")
SESSION_TABLE = os.environ.get("SESSION_TABLE", "SessionTracking")


def _utc_now():
    """Return ISO 8601 UTC timestamp with Z suffix."""
    return datetime.utcnow().isoformat() + "Z"



def save_course(course_detail: dict, course_name: str):
    """Save a course (only once per course_id)."""
    now = _utc_now()

    dynamodb.put_item(
        TableName=COURSE_TABLE,
        Item={
            "course_id": {"N": str(course_detail["course_id"])},
            "course_name": {"S": course_name},
            "course_detail": {"M": _dict_to_dynamodb(course_detail)},
            "total_videos": {"N": str(course_detail.get("total_videos", 0))},
            "created_at": {"S": now},
        },
    )
    print(f"Saved course: {course_name} ({course_detail['course_id']})")



def save_session(session_id, course_id, topic_id, topic_title, node, status):
    """Save a session record for a specific topic/video."""
    now = _utc_now()

    dynamodb.put_item(
        TableName=SESSION_TABLE,
        Item={
            "session_id": {"S": session_id},
            "course_id": {"N": str(course_id)},
            "topic_id": {"N": str(topic_id)},
            "topic_title": {"S": topic_title},
            "status": {"S": status},
            "node": {"S": node},
            "created_at": {"S": now},
            "updated_at": {"S": now},
        },
    )
    print(f"Saved session {session_id} for course {course_id} - topic {topic_id}")



def update_session(session_id, status=None, node=None):
    """Update session progress (status, node, timestamp)."""
    now = _utc_now()

    expr_attr_names = {"#ut": "updated_at"}
    expr_attr_values = {":u": {"S": now}}
    update_expr = ["#ut = :u"]

    if status:
        expr_attr_names["#st"] = "status"
        expr_attr_values[":s"] = {"S": status}
        update_expr.append("#st = :s")

    if node:
        expr_attr_names["#nd"] = "node"
        expr_attr_values[":n"] = {"S": node}
        update_expr.append("#nd = :n")

    dynamodb.update_item(
        TableName=SESSION_TABLE,
        Key={"session_id": {"S": session_id}},
        UpdateExpression="SET " + ", ".join(update_expr),
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_attr_values,
    )
    print(f"✅ Updated session {session_id}: node={node}, status={status}")


# 🔧 Optional Helpers
def get_course(course_id: int):
    """Fetch a course record by course_id."""
    response = dynamodb.get_item(
        TableName=COURSE_TABLE,
        Key={"course_id": {"N": str(course_id)}}
    )
    return response.get("Item")


def get_session(session_id: str):
    """Fetch a session record by session_id."""
    response = dynamodb.get_item(
        TableName=SESSION_TABLE,
        Key={"session_id": {"S": session_id}}
    )
    return response.get("Item")


def _dict_to_dynamodb(data):
    """Recursively convert dict/list into DynamoDB structure."""
    if isinstance(data, dict):
        return {"M": {k: _dict_to_dynamodb(v) for k, v in data.items()}}
    elif isinstance(data, list):
        return {"L": [_dict_to_dynamodb(v) for v in data]}
    elif isinstance(data, str):
        return {"S": data}
    elif isinstance(data, bool):
        return {"BOOL": data}
    elif isinstance(data, (int, float)):
        return {"N": str(data)}
    elif data is None:
        return {"NULL": True}
    else:
        raise TypeError(f"Unsupported type: {type(data)}")
