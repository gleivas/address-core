from http import HTTPStatus

import pytest
from mock import patch

from address_core.services import PreciselyApiServiceError

with patch('boto3.client') as mock_method:
    from address_core.endpoints import AddressEndpoint


class RequestBuilder:
    def __init__(self, endpoint, http_method='GET', query_string_parameter=None):
        self.request = {
            'resource': endpoint,
            'path': endpoint,
            'httpMethod': http_method,
            'headers': {},
            'multiValueHeaders': None,
            'queryStringParameters': query_string_parameter,
            'multiValueQueryStringParameters': None,
            'pathParameters': {},
            'stageVariables': None,
            'requestContext': {},
            'body': {},
            'isBase64Encoded': False
        }

    def build(self):
        return self.request


@pytest.fixture
def address_endpoint(mocker):
    endpoint = AddressEndpoint(precisely_api_service=mocker.MagicMock())
    endpoint.precisely_api_service.get_locations.return_value = {}
    return endpoint


def test_should_process_address_endpoint(address_endpoint):
    # GIVEN
    request = RequestBuilder("/address", query_string_parameter={'search_text': 'text'}).build()

    # WHEN
    response = address_endpoint(request, None)

    # THEN
    assert response['statusCode'] == HTTPStatus.OK


def test_should_not_process_address_endpoint_due_to_method_not_allowed(address_endpoint):
    # GIVEN
    request = RequestBuilder("/address", http_method='POST', query_string_parameter={'search_text': 'text'}).build()

    # WHEN
    response = address_endpoint(request, None)

    # THEN
    assert response['statusCode'] == HTTPStatus.METHOD_NOT_ALLOWED


def test_should_not_process_address_endpoint_due_to_internal_server_error(address_endpoint):
    # GIVEN
    address_endpoint.precisely_api_service.get_locations.side_effect = Exception
    request = RequestBuilder("/address", http_method='GET', query_string_parameter={'search_text': 'text'}).build()

    # WHEN
    response = address_endpoint(request, None)

    # THEN
    assert response['statusCode'] == HTTPStatus.INTERNAL_SERVER_ERROR


def test_should_not_process_address_endpoint_due_to_precisely_api_service_error(address_endpoint):
    # GIVEN
    address_endpoint.precisely_api_service.get_locations.side_effect = PreciselyApiServiceError
    request = RequestBuilder("/address", http_method='GET', query_string_parameter={'search_text': 'text'}).build()

    # WHEN
    response = address_endpoint(request, None)

    # THEN
    assert response['statusCode'] == HTTPStatus.UNPROCESSABLE_ENTITY
