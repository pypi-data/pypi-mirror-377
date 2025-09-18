import boto3
import os
from datetime import datetime

dynamodb = boto3.client("dynamodb", region_name="ap-south-1")
TABLE_NAME = os.environ.get("TRACKER_TABLE", "SessionTracking")


def update_session(session_id, node, status):
    now = datetime.utcnow().isoformat()

    # Alias reserved keyword 'status' with #st
    expr_attr_names = {
        "#st": "status",
        "#nd": "node",
        "#ut": "updated_at",
    }

    expr_values = {
        ":s": {"S": status},
        ":n": {"S": node},
        ":u": {"S": now},
    }

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"session_id": {"S": session_id}},
        UpdateExpression="SET #st = :s, #nd = :n, #ut = :u",
        ExpressionAttributeNames=expr_attr_names,
        ExpressionAttributeValues=expr_values,
    )
    print(f"Updated session {session_id}: node={node}, status={status}")
