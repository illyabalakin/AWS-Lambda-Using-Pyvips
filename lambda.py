#!/usr/bin/python
import pyvips


def lambda_handler(event, context):
    return 'Hello illya...  from pyvips AWS Lambda'


if __name__ == "__main__":
    event = {
        "params": {
            "action": "test",
            "s3bucket": "mybucket",
            "s3key": "orig.jpg"
        },
        "key2": "value2",
        "key1": "value1"
    }
    context = None
    lambda_handler(event, context)
