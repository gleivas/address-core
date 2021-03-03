import argparse
import os
from pprint import pprint

import requests


def call_api(search_text):
    api_key = os.environ.get('api_key')
    url = 'https://855qezwla0.execute-api.us-east-1.amazonaws.com/v1/address?search_text='
    headers = {'x-api-key': api_key}
    params = {'search_text': search_text}
    response = requests.get(url, headers=headers, params=params)
    pprint(response.json())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search_text", help="The fragment of address that will be looked for",
                        type=str, default='6636 AVENUE J')
    args = parser.parse_args()
    call_api(args.search_text)
