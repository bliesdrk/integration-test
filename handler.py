"""
Process messages from an SQS queue and publish them to an SNS topic.
"""
from typing import Any, Dict
import json
import os
import boto3
from botocore.exceptions import ClientError

def process_queue(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Process messages from an SQS queue and publish them to an SNS topic.

    Args:
        event (Dict[str, Any]): The Lambda event containing SQS records
                               Expected format:
                               {
                                   "Records": [
                                       {
                                           "body": "message content"
                                       }
                                   ]
                               }

    Returns:
        Dict[str, Any]: Response object with status code and message
                        Format:
                        {
                            "statusCode": 200,
                            "body": "{\"message\": \"Processing complete\"}"
                        }

    Raises:
        ClientError: If there is an error publishing to SNS
        Exception: If there is an error processing the message

    Environment Variables:
        TOPIC_ARN: The ARN of the SNS topic to publish to

    The function:
    1. Iterates through SQS records in the event
    2. Takes the message body from each record
    3. Creates a response object with the input value
    4. Publishes the response to an SNS topic
    5. Returns a success response when complete
    """
    # Initialize SNS client
    sns = boto3.client('sns')
    topic_arn = os.environ['TOPIC_ARN']

    for record in event['Records']:
        try:
            # Get the input value directly from the message body
            input_value = record['body']

            # Process the message
            response = {
                'out': input_value
            }

            # Publish to SNS topic
            try:
                sns_response = sns.publish(
                    TopicArn=topic_arn,
                    Message=json.dumps(response),
                    MessageAttributes={
                        'MessageType': {
                            'DataType': 'String',
                            'StringValue': 'ProcessedMessage'
                        }
                    }
                )
                print(f"Message published to SNS. MessageId: {sns_response['MessageId']}")

            except ClientError as e:
                print(f"Error publishing to SNS: {str(e)}")
                raise

            print(f"{context.function_name} processed message: {json.dumps(response)}")

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            raise

    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Processing complete'})
    }
