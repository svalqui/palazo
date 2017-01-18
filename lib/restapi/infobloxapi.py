# Source Class
# https://ipam.unimelb.edu.au/wapi/v2.2.2/

import requests
from requests.auth import HTTPBasicAuth
import lib.restapimaster
import json


class IB(lib.restapimaster.RestApi):
    def __init__(self, user_name, password):
        super(IB, self).__init__()
        self.user_name = user_name
        self.password = password
        self.urlbase = "https://myipam/wapi/v2.2.2/"
        self.url_queried = self.urlbase + 'network?_paging=1&_return_as_object=1&_max_results=5'
        self.page = requests.get(self.url_queried, verify=False,
                                 auth=HTTPBasicAuth(self.user_name, self.password))
        print(self.page.status_code)
        if len(self.page.headers) > 0:
            print(" Page headers")
            for key in self.page.headers.keys():
                print(key, " -value: ", self.page.headers[key])

        self.page_decoded = json.loads(self.page.text)

        self.navigate_json(self.page_decoded)
