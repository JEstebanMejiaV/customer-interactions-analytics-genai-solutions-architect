from constructs import Construct
from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    aws_lambda as _lambda,
    aws_apigateway as apigw,
)


class InteractionsStack(Stack):
    """
    Minimal CDK stack to show how this API could be deployed on AWS.


    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        table = dynamodb.Table(
            self,
            "InteractionsTable",
            partition_key=dynamodb.Attribute(
                name="account_number",
                type=dynamodb.AttributeType.STRING,
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING,
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )
        """ 
        # Lambda super simple que ilustra el wiring de API Gateway + Lambda.
        # En un escenario real, aquí se usaría la misma lógica de la API
        # (por ejemplo, con un handler adaptado a DynamoDB
        """

        fn = _lambda.Function(
            self,
            "InteractionsFunction",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="lambda_handler.main",
            code=_lambda.Code.from_asset("../lambda"),
            environment={
                "TABLE_NAME": table.table_name,
            },
        )

        table.grant_read_data(fn)

        api = apigw.LambdaRestApi(
            self,
            "InteractionsApi",
            handler=fn,
            proxy=False,
            rest_api_name="InteractionsApi",
            description="Minimal Interactions API for a technical challenge",
        )

        interactions = api.root.add_resource("interactions")
        account = interactions.add_resource("{account_number}")
        account.add_method("GET")
