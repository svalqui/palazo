#
# http://www.macvendorlookup.com/api/v2/{MAC_Address}

import requests
import lib.restapimaster
import time


class QueryMac(lib.restapimaster.RestApi):
    def __init__(self):
        super(QueryMac, self).__init__()
        self.urlbase = "http://api.macvendors.com/"
        # self.urlbase = "http://www.macvendorlookup.com/api/v2/"
        self.url_queried = ""
        self.list_content = []
        self.page = ""
        self.page_text = ""
        self.current_page = ""
        self.mac_manufacturer = ""

    def read_page(self, mac="", debug=False):
        self.url_queried = self.urlbase + mac
        if debug:
            print("reading ...", self.url_queried)
        self.page = requests.get(self.url_queried)
        time.sleep(0.1)
        if debug:
            print("Querying :  ", self.url_queried)
            print(self.page.status_code)
            if len(self.page.headers) > 0:
                for key in self.page.headers.keys():
                    print(key, " -value: ", self.page.headers[key])
        if self.page.status_code == 200:
            self.page_text = self.page.text
        return self.page_text

    def mac_company(self, mac="", debug=False):
        self.mac_manufacturer = ""
        self.mac_manufacturer = self.read_page(mac)
        return self.mac_manufacturer


















# self.urlbase = "http://www.macvendorlookup.com/api/v2/"





# - L-Content : list here
# - L-Content : dict found on list resending
# country - D_Content : str Value : UNITED STATES
# company - D_Content : str Value : Dell Inc
# endDec - D_Content : str Value : 26403110125567
# endHex - D_Content : str Value : 180373FFFFFF
# addressL3 - D_Content : str Value : Round Rock Texas 78682
# startDec - D_Content : str Value : 26403093348352
# addressL2 - D_Content : str Value :
# addressL1 - D_Content : str Value : One Dell Way, MS:RR5-45
# startHex - D_Content : str Value : 180373000000
# type - D_Content : str Value : MA-L
