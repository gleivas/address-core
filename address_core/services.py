import base64
import os
from datetime import datetime, timedelta

import boto3
import requests


class PreciselyApiService:

    def __init__(self, ssm_client=None):
        self._ssm = ssm_client if ssm_client else boto3.client('ssm')
        self._session = requests.session()
        self._api_key = self._get_api_key()
        self._api_secret = self._get_api_secret()
        self._base_url = 'https://api.precisely.com'
        self._expires_in = datetime.now()

        self._oauth_endpoint = 'oauth/token'
        self._typehead_endpoint = 'typeahead/v1/locations'

    def get_locations(self, params):
        default_params = {
            'latitude': 31.968600,
            'longitude': -99.901800,
            'searchRadius': 1000,
            'searchRadiusUnit': 'miles',
            'maxCandidates': 10,
            'returnAdminAreasOnly': 'N',
            'includeRangesDetails': 'Y',
            'country': 'usa',
            'areaName1': 'tx',
            'matchOnAddressNumber': True
        }
        default_params.update(params)
        endpoint = self._typehead_endpoint
        addresses = self._get(endpoint, default_params).json()
        return self._format_addresses(addresses)

    @staticmethod
    def _format_addresses(addresses):
        formatted_addresses = []
        for address_info in addresses['location']:
            address = address_info['address']
            ranges = address_info.get('ranges')
            if not ranges:
                formatted_addresses.append(address['formattedAddress'])
            else:
                for address_range in ranges:
                    for unit in address_range.get('units'):
                        formatted_addresses.append(unit['formattedUnitAddress'])
        return formatted_addresses

    def _get(self, endpoint, params):
        if datetime.now() >= self._expires_in:
            self._refresh_token()
        return self._session.get(f'{self._base_url}/{endpoint}', params=params)

    def _refresh_token(self):
        basic_auth = base64.b64encode(f'{self._api_key}:{self._api_secret}'.encode())
        headers = {'Authorization': f'Basic {basic_auth.decode()}'}
        body = {'grant_type': 'client_credentials'}
        url = f'{self._base_url}/{self._oauth_endpoint}'
        response = requests.post(url=url, data=body, headers=headers).json()
        self._session.headers.update({'Authorization': f'Bearer {response.get("access_token")}'})
        self._expires_in = datetime.now() + timedelta(seconds=int(response.get('expiresIn')))

    def _get_parameter(self, param, with_decryption=True):  # pragma no cover
        return self._ssm.get_parameter(Name=param, WithDecryption=with_decryption)['Parameter']['Value']

    def _get_api_key(self):  # pragma no cover
        return self._get_parameter(os.environ.get('precisely_api_key', 'api_key'))

    def _get_api_secret(self):  # pragma no cover
        return self._get_parameter(os.environ.get('precisely_api_secret', 'api_secret'))
