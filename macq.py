from lib.restapi.maclookapi import QueryMac


input_mac = input('Mac Address: ')
mac_address = QueryMac().mac_company(input_mac)