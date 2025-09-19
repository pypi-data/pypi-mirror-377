import os
import json

from lib import logging_


def handler(event, context):
    logger = logging_.setup(request_id=context.aws_request_id, level=os.getenv("LOG_LEVEL", "INFO"))

    result = {"account_batches": []}
    return result
