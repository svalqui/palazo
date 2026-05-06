#!/usr/bin/env python
import logging
import json
import time
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter, Namespace
import os
from falconpy import Hosts
import sys

def main():
    """ CLI implementation temporal for fast trial while developing
    """

    hosts = Hosts(client_id=os.getenv("FALCON_CLIENT_ID"),
                  client_secret=os.getenv("FALCON_CLIENT_SECRET"),
                  base_url=os.getenv("FALCON_API_URL"),
                  )

    SEARCH_FILTER = "s-l-z"

    # Retrieve a list of hosts that have a hostname that matches our search filter
    hosts_search_result = hosts.query_devices_by_filter(filter=f"hostname:*'*{SEARCH_FILTER}*'")

    # Confirm we received a success response back from the CrowdStrike API
    if hosts_search_result["status_code"] == 200:
        hosts_found = hosts_search_result["body"]["resources"]  # list of device IDs
        # print(type(hosts_found))
        # print(hosts_found)
        # Confirm our search produced results
        if hosts_found:
            # Retrieve the details for all matches
            hosts_detail = hosts.get_device_details(ids=hosts_found)["body"]["resources"]  # List of Dict
            # print('---')
            # print(hosts_detail)

            for detail in hosts_detail:
                # Display the AID and hostname for this match
                print('++++++++++++')
                # for k in detail.keys():
                #    print("  ", k, detail[k])
                aid = detail["device_id"]
                hostname = detail["hostname"]
                ip = detail["local_ip"]
                osv = detail["os_version"]
                print(f"{hostname} ({aid}) {ip} {osv}")
        else:
            print("No hosts found matching that hostname within your Falcon tenant.")
    else:
        # Retrieve the details of the error response
        error_detail = hosts_search_result["body"]["errors"]
        for error in error_detail:
            # Display the API error detail
            error_code = error["code"]
            error_message = error["message"]
            print(f"[Error {error_code}] {error_message}")

if __name__ == '__main__':
    sys.exit(main())
