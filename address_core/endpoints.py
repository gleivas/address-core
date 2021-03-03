import logging
import os
from http import HTTPStatus

from address_core.abstract_api import AbstractApi, HttpMethods, lambda_handler
from address_core.services import PreciselyApiService, PreciselyApiServiceError

LOGGER = logging.getLogger()
LOGGER.setLevel(getattr(logging, os.environ.get('log_level', 'INFO')))


@lambda_handler
class AddressApi(AbstractApi):
    def __init__(self, precisely_api_service=None):
        super().__init__()
        self.precisely_api_service = precisely_api_service if precisely_api_service else PreciselyApiService()
        self.register_endpoint(HttpMethods.GET, '/address', self.get_addresses)

    def get_addresses(self):
        try:
            search_text = self.event.query_parameters.get('search_text')
            if not search_text:
                message = {'message': 'missing required query parameter search_text'}
                return self.format_response(HTTPStatus.BAD_REQUEST, message)
            LOGGER.info(f'Search Text: {search_text}')
            params = {'searchText': search_text}
            response = self.precisely_api_service.get_locations(params)
            return self.format_response(HTTPStatus.OK, response)
        except PreciselyApiServiceError as error:
            return self.format_response(HTTPStatus.UNPROCESSABLE_ENTITY, {'error': str(error)})
