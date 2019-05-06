# Copyright 2019 by Sergio Valqui. All rights reserved.
# Source Class
# https://
# https://ipam.illinois.edu/wapidoc/objects/network.html
# https://ipam.illinois.edu/wapidoc/objects/range.html
# to add a MAC to a given filter use POST
# macfilteraddress?filter=filter-name&mac=


import requests
from requests.auth import HTTPBasicAuth
import restapi.restapimaster
import json


class IB(restapi.restapimaster.RestApi):
    def __init__(self, user_name, password, host_name, ipam_object=""):
        super(IB, self).__init__()
        self.user_name = user_name
        self.password = password
        self.urlbase = "https://" + host_name + "/wapi/v2.2.2/"
        self.object_queried = ipam_object
        self.url_queried = ""
        self.url_posted = ""
        self.page = ""
        self.pages = ""
        self.page_decoded = ""
        self.next_page_id = ""
        self.querying = ""
        self.posting = ""
        self.page_id = ""

    def get_page(self):
        self.next_page_id = ""
        self.url_queried = self.urlbase + self.querying
        self.page = requests.get(self.url_queried, verify=False,
                                 auth=HTTPBasicAuth(self.user_name, self.password))
        print("Query: ", self.url_queried)
        print(self.page.status_code)
        if len(self.page.headers) > 0:
            print("---- Page headers ***************")
            for key in self.page.headers.keys():
                print(key, " -value: ", self.page.headers[key])
            print("---- End page headers.. *********")

        self.page_decoded = json.loads(self.page.text)  # Returns Dict
#        self.pages += self.page_decoded
        if "next_page_id" in self.page_decoded:
            self.next_page_id = self.page_decoded["next_page_id"]
            print("-Next Page ID: ", self.next_page_id)
#        print(self.page_decoded.__type__)
        print(self.page_decoded.keys())
#        print(self.page_decoded["result"].keys())
        for record in self.page_decoded["result"]:
            print(record.keys())
            #print(record["macfilteraddress"])
            #print(record["network"], " ", record["comment"])
            #print(record)
        return self.next_page_id

    def get_page_handler(self):
        # permission
        self.querying = self.object_queried + "?_paging=1&_return_as_object=1&_max_results=1000"
        print("##############")
        self.page_id = self.get_page()
        while self.page_id != "":
            print("   ##############")
            self.querying = self.object_queried + "?_page_id=" + self.next_page_id
            self.page_id = self.get_page()

    def post_page(self, post_detail=""):
        self.posting = self.object_queried + post_detail
        self.url_posted = self.urlbase + self.posting
        self.page = requests.post(self.url_posted, verify=False,
                                  auth=HTTPBasicAuth(self.user_name, self.password))
        print("Posting: ", self.url_posted)
        print(self.page.status_code)
        if len(self.page.headers) > 0:
            print("---- Page headers ***************")
            for key in self.page.headers.keys():
                print(key, " -value: ", self.page.headers[key])
            print("---- End page headers.. *********")
        return self.page.status_code

    def add_mac_to_macfilter(self, filter_name="", mac_address=""):
        self.object_queried = "macfilteraddress"
        post_detail = "?filter=" + filter_name + "&mac=" + mac_address
        self.post_page(post_detail)

        # self.navigate_json(self.page_decoded)
