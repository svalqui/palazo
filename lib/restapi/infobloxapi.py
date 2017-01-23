# Source Class
# https://ipam.unimelb.edu.au/wapi/v2.2.2/

import requests
from requests.auth import HTTPBasicAuth
import lib.restapimaster
import json


class IB(lib.restapimaster.RestApi):
    def __init__(self, user_name, password, host_name):
        super(IB, self).__init__()
        self.user_name = user_name
        self.password = password
        self.urlbase = "https://" + host_name + "/wapi/v2.2.2/"
        self.url_queried = ""
        self.page = ""
        self.page_decoded = ""
        self.next_page_id = ""
        self.querying = ""
        self.page_id = ""

    def read_page(self):
        self.next_page_id = ""
        self.url_queried = self.urlbase + self.querying
        self.page = requests.get(self.url_queried, verify=False,
                             auth=HTTPBasicAuth(self.user_name, self.password))
        print("Query: ", self.url_queried)
        print(self.page.status_code)
        if len(self.page.headers) > 0:
            print(" Page headers ***************")
            for key in self.page.headers.keys():
                print(key, " -value: ", self.page.headers[key])
            print(" End page headers.. *********")

        self.page_decoded = json.loads(self.page.text)
        if "next_page_id" in self.page_decoded:
            self.next_page_id = self.page_decoded["next_page_id"]
            print(self.next_page_id)
        #print(self.page_decoded["result"].keys())
        for record in self.page_decoded["result"]:
            print(record["network"], " ", record["comment"])
        return self.next_page_id

    def page_handler(self):
        #network
        self.querying = "permission?_paging=1&_return_as_object=1&_max_results=1000"
        print("##############")
        self.page_id = self.read_page()
        while self.page_id != "":
            print("   ##############")
            self.querying = "network?_page_id=" + self.next_page_id
            self.page_id = self.read_page()



        #self.navigate_json(self.page_decoded)
