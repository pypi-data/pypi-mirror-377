import boto3
from datetime import datetime

dynamodb = boto3.client("dynamodb")
TABLE_NAME = "SessionTracking"

def update_session(session_id, node, status, details=None):
    """Update or create session tracking entry"""
    update_expr = "SET current_node=:n, status=:s, last_updated=:t"
    expr_values = {
        ":n": {"S": node},
        ":s": {"S": status},
        ":t": {"S": datetime.utcnow().isoformat()}
    }

    if details:
        update_expr += ", details=:d"
        expr_values[":d"] = {"S": str(details)}

    dynamodb.update_item(
        TableName=TABLE_NAME,
        Key={"session_id": {"S": session_id}},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values
    )
