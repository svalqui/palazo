from lib.restapi.maclookapi import QueryMac

input_mac = input('Mac Address: ')
manufacturer = QueryMac().mac_company(input_mac)
print(manufacturer)