#!/usr/bin/env python
# https://github.com/dell/OpenManage-Enterprise/blob/main/docs/python_library_code.md#interact-with-an-api-resource

import json
from os import path
import requests

import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

API_ENDPOINT = "https://"
BASELINES_SRV = "/api/UpdateService/Baselines"

def authenticate(ome_ip_address: str, ome_username: str, ome_password: str) -> dict:
    """
    Authenticates with OME and creates a session

    Args:
        ome_ip_address: IP address of the OME server
        ome_username:  Username for OME
        ome_password: OME password

    Returns: A dictionary of HTTP headers

    Raises:
        Exception: A generic exception in the event of a failure to connect
    """

    authenticated_headers = {'content-type': 'application/json'}
    session_url = 'https://%s/api/SessionService/Sessions' % ome_ip_address
    user_details = {'UserName': ome_username,
                    'Password': ome_password,
                    'SessionType': 'API'}
    try:
        session_info = requests.post(session_url, verify=False,
                                     data=json.dumps(user_details),
                                     headers=authenticated_headers)
    except requests.exceptions.ConnectionError:
        print(
            "Failed to connect to OME. This typically indicates a network connectivity problem. Can you ping OME?")
        sys.exit(0)

    if session_info.status_code == 201:
        authenticated_headers['X-Auth-Token'] = session_info.headers['X-Auth-Token']
        return authenticated_headers

    print(
        "There was a problem authenticating with OME. Are you sure you have the right username, password, "
        "and IP?")
    raise Exception(
        "There was a problem authenticating with OME. Are you sure you have the right username, "
        "password, and IP?")


def get_data(authenticated_headers: dict, url: str, odata_filter: str = None, max_pages: int = None) -> dict:
    """
    This function retrieves data from a specified URL. Get requests from OME return paginated data. The code below
    handles pagination. This is the equivalent in the UI of a list of results that require you to go to different
    pages to get a complete listing.

    Args:
        authenticated_headers: A dictionary of HTTP headers generated from an authenticated session with OME
        url: The API url against which you would like to make a request
        odata_filter: An optional parameter for providing an odata filter to run against the API endpoint.
        max_pages: The maximum number of pages you would like to return

    Returns: Returns a dictionary of data received from OME

    """

    next_link_url = None

    if odata_filter:
        count_data = requests.get(url + '?$filter=' + odata_filter, headers=authenticated_headers, verify=False)

        if count_data.status_code == 400:
            print("Received an error while retrieving data from %s:" % url + '?$filter=' + odata_filter)
            pprint(count_data.json()['error'])
            return {}

        count_data = count_data.json()
        if count_data['@odata.count'] <= 0:
            print("No results found!")
            return {}
    else:
        count_data = requests.get(url, headers=authenticated_headers, verify=False).json()

    if 'value' in count_data:
        data = count_data['value']
    else:
        data = count_data

    if '@odata.nextLink' in count_data:
        # Grab the base URI
        next_link_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url)) + count_data['@odata.nextLink']

    i = 1
    while next_link_url is not None:
        # Break if we have reached the maximum number of pages to be returned
        if max_pages:
            if i >= max_pages:
                break
            else:
                i = i + 1
        response = requests.get(next_link_url, headers=authenticated_headers, verify=False)
        next_link_url = None
        if response.status_code == 200:
            requested_data = response.json()
            if requested_data['@odata.count'] <= 0:
                print("No results found!")
                return {}

            # The @odata.nextLink key is only present in data if there are additional pages. We check for it and if it
            # is present we get a link to the page with the next set of results.
            if '@odata.nextLink' in requested_data:
                next_link_url = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(url)) + \
                                requested_data['@odata.nextLink']

            if 'value' in requested_data:
                data += requested_data['value']
            else:
                data += requested_data
        else:
            print("Unknown error occurred. Received HTTP response code: " + str(response.status_code) +
                    " with error: " + response.text)
            raise Exception("Unknown error occurred. Received HTTP response code: " + str(response.status_code)
                            + " with error: " + response.text)

    return data


def main():
    ome_address = input("OME address: ")
    ome_u = input("OME user: ")
    ome_p = input("OME pass")

    auth_header = authenticate(ome_address, ome_u, ome_p)

    url = API_ENDPOINT + ome_address + BASELINES_SRV

    base_lines = get_data(auth_header, url ,None,1000)
    for d in base_lines:
        print(d)


if __name__ == '__main__':
    sys.exit(main())

