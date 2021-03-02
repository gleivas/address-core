import json
import logging
import os
import sys
from enum import Enum
from http import HTTPStatus

LOGGER = logging.getLogger()
LOGGER.setLevel(getattr(logging, os.environ.get('log_level', 'INFO')))


def lambda_handler(func):
    module = func.__module__
    handler_name = f'{func.__name__}Handler'
    setattr(sys.modules[module], handler_name, func())
    return func


class HttpMethods(Enum):
    GET = 'GET'
    DELETE = 'DELETE'
    PATCH = 'PATCH'
    POST = 'POST'
    PUT = 'PUT'


class Event:
    def __init__(self, event):
        self.resource = event['resource']
        self.path = event['path']
        self.method = HttpMethods(event['httpMethod'])
        self.headers = event.get('headers', {})
        self.query_parameters = event.get('queryStringParameters', {})
        self.body = json.loads(event['body']) if event['body'] else None


class AbstractApi:
    def __init__(self):
        self.actions = {}
        self.event = None

    def __call__(self, event, context):
        return self.process_event(event, context)

    def process_event(self, event, context):
        try:
            self.event = Event(event)
            action = self.actions.get((self.event.method, self.event.resource))
            if not action:
                message = f'Method {self.event.method} is not allowed on {self.event.resource}'
                return self.format_response(HTTPStatus.METHOD_NOT_ALLOWED, {'message': message})
            return action()
        except Exception as error:
            LOGGER.error(f'Error: {error}')
            message = 'Internal Server Error'
            return self.format_response(HTTPStatus.INTERNAL_SERVER_ERROR, {'message': message})

    def register_action(self, http_method, path, action):
        self.actions[(http_method, path)] = action

    @staticmethod
    def format_response(status_code, body=None, headers=None):
        return {
            'isBase64Encoded': False,
            'statusCode': status_code,
            'headers': headers if headers else {'Content-Type': 'application/json'},
            'body': json.dumps(body) if body else None
        }
