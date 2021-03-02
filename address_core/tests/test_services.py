from datetime import datetime

import pytest
import requests_mock

from address_core.services import PreciselyApiService

BASE_URL = 'https://api.precisely.com'
TYPEHEAD_URL = f'{BASE_URL}/typeahead/v1/locations'
OAUTH_URL = f'{BASE_URL}/oauth/token'


@pytest.fixture
def precisely_api_service(mocker):
    with requests_mock.Mocker() as mock:
        mock.post(
            OAUTH_URL,
            json={
                "access_token": "{YOUR ACCESS TOKEN}",
                "tokenType": "BearerToken",
                "issuedAt": "1429188455329",
                "expiresIn": "35999",
                "clientID": "{YOUR API KEY}",
                "org": "api.precisely.com"
            }
        )
        return PreciselyApiService(mocker.MagicMock())


def test_should_refresh_token_when_initialize(mocker):
    # GIVEN
    # WHEN
    with requests_mock.Mocker() as mock:
        mock.post(
            OAUTH_URL,
            json={
                "access_token": "{YOUR ACCESS TOKEN}",
                "tokenType": "BearerToken",
                "issuedAt": "1429188455329",
                "expiresIn": "35999",
                "clientID": "{YOUR API KEY}",
                "org": "api.precisely.com"
            }
        )
        service = PreciselyApiService(mocker.MagicMock())

    # THEN
    assert service._session.headers.get('Authorization')


def test_should_refresh_token_when_expired(mocker, precisely_api_service):
    # GIVEN
    begin_expires_in = datetime.now()
    precisely_api_service._expires_in = begin_expires_in

    # WHEN
    with requests_mock.Mocker() as mock:
        mock.get(
            f'{BASE_URL}/test',
            json={}
        )
        mock.post(
            OAUTH_URL,
            json={
                "access_token": "{YOUR ACCESS TOKEN}",
                "tokenType": "BearerToken",
                "issuedAt": "1429188455329",
                "expiresIn": "35999",
                "clientID": "{YOUR API KEY}",
                "org": "api.precisely.com"
            }
        )
        precisely_api_service._get('test', {})

    # THEN
    assert begin_expires_in != precisely_api_service._expires_in


def test_should_get_locations_formatted_with_apartments(precisely_api_service):
    # GIVEN
    formatted_address = '1618 Park Ave, Abilene, TX 79603'
    expected_api_response = {
        'location': [
            {
                'address': {
                    'formattedAddress': formatted_address, 'mainAddressLine': '1618 Park Ave',
                    'addressLastLine': 'Abilene, TX 79603', 'placeName': '', 'areaName1': 'TX', 'areaName2': '',
                    'areaName3': 'Abilene', 'areaName4': '', 'postCode': '79603', 'postCodeExt': '',
                    'country': 'USA', 'addressNumber': '1618', 'streetName': 'Park Ave', 'unitType': '',
                    'unitValue': ''
                },
                'distance': {'unit': 'MILES', 'value': '34.459'},
                'geometry': {'type': 'Point', 'coordinates': [-99.75059, 32.462575]},
                'totalUnitCount': 0, 'ranges': []
            },
            {'address': {'formattedAddress': '1618 Parker Ln, Apt A, Austin, TX 78741',
                         'mainAddressLine': '1618 Parker Ln', 'addressLastLine': 'Austin, TX 78741', 'placeName': '',
                         'areaName1': 'TX', 'areaName2': '', 'areaName3': 'Austin', 'areaName4': '',
                         'postCode': '78741', 'postCodeExt': '', 'country': 'USA', 'addressNumber': '1618',
                         'streetName': 'Parker Ln', 'unitType': '', 'unitValue': ''},
             'distance': {'unit': 'MILES', 'value': '175.264'},
             'geometry': {'type': 'Point', 'coordinates': [-97.73688, 30.231054999999998]}, 'totalUnitCount': 2,
             'ranges': [{'placeName': '', 'units': [
                 {'unitInfo': 'Apt A', 'formattedUnitAddress': '1618 Parker Ln, Apt A, Austin, TX 78741'},
                 {'unitInfo': 'Apt B', 'formattedUnitAddress': '1618 Parker Ln, Apt B, Austin, TX 78741'}]}]}
        ]
    }

    # WHEN
    with requests_mock.Mocker() as mock:
        mock.get(
            TYPEHEAD_URL,
            json=expected_api_response
        )
        response = precisely_api_service.get_locations({})

    # THEN
    assert len(response) == 3
    assert response[0] == formatted_address
