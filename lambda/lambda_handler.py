import json
import os


def main(event, context):
    """
    Minimal Lambda handler used only by the CDK example.

    handler  simple para no mezclar la lógica de la API en contenedor con la 
    versión Lambda. Su único propósito
    es mostrar la estructura API Gateway + Lambda + DynamoDB.
    """
    account_number = event.get("pathParameters", {}).get(
        "account_number", "unknown")
    table_name = os.getenv("TABLE_NAME", "InteractionsTable")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(
            {
                "message": "Hello from Lambda backing Interactions API",
                "account_number": account_number,
                "table": table_name,
                "note": "This is a placeholder Lambda handler for CDK demo only.",
            }
        ),
    }
