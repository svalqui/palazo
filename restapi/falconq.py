#!/usr/bin/env python
import logging
import json
import time
from datetime import datetime
from argparse import ArgumentParser, RawTextHelpFormatter, Namespace
import os
from falconpy import Hosts, SpotlightVulnerabilities
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

    # query hosts by subnet

    hosts_in_subnet = hosts.query_devices_by_filter(filter="local_ip:'45.113.232.0/22'",
                                                    limit=5000,
                                                    offset=0)
    print(type(hosts_in_subnet))
    print()

    # Extract asset IDs
    asset_ids = hosts_in_subnet["body"]["resources"]

    print(f"Found {len(asset_ids)} assets")
    print()
    print(asset_ids[0])
    print()

    # Query vulnerabilities

    # Initialise the Spotlight client
    vul_client = SpotlightVulnerabilities(
        client_id=os.getenv("FALCON_CLIENT_ID"),
        client_secret=os.getenv("FALCON_CLIENT_SECRET"),
        base_url=os.getenv("FALCON_API_URL"),
    )

    print("---- Vulnerabilities")

    # Query all vulnerabilities first
    facet = {"cve", "host_info", "remediation", "evaluation_logic"}

    # Base filters
    base_filter = "status:!'closed'+last_seen_within:'3'+cve.exprt_rating:['CRITICAL']+cve.severity:['CRITICAL']+host_info.internet_exposure:'Yes'"
    # print(asset_ids[0])

    # Build aid filter with array
    aid_list = ",".join([f"'{aid}'" for aid in asset_ids])
    aid_filter = f"aid:[{aid_list}]"

    SEARCH_FILTER_TEST = f"{base_filter}+{aid_filter}"

    vul_results = vul_client.query_vulnerabilities_combined(
        filter=SEARCH_FILTER_TEST,
        facet=facet,
        limit=400
    )

    vulnerabilities = vul_results["body"]["resources"]
    print(f"Total vulnerabilities: {len(vulnerabilities)}")

    # Get all unique AIDs in the vulnerabilities
    vuln_aids = set(vuln.get("aid") for vuln in vulnerabilities)

    print(f"AIDs in vulnerabilities: {len(vuln_aids)}")
    print(f"AIDs in asset_ids: {len(asset_ids)}")
    print()

    # Group by asset
    vulns_by_asset = {}
    for vuln in vulnerabilities:
        aid = vuln.get("aid")
        if aid not in vulns_by_asset:
            vulns_by_asset[aid] = []
        vulns_by_asset[aid].append(vuln)

    # Print vulnerabilities per asset
    for asset_id in asset_ids:
        count = len(vulns_by_asset.get(asset_id, []))
        print(f"{asset_id}: {count} vulnerabilities")

#    # Check the structure of a sample vulnerability
#    if vulnerabilities:
#        print("\nSample vulnerability structure:")
##        print(vulnerabilities[0].keys())
        print(f"\naid value: {vulnerabilities[0].get('aid')}")

    print(f"Total vulnerabilities: {len(vulnerabilities)}")
    print(f"Total assets: {len(asset_ids)}\n")

    # Group vulnerabilities by aid (asset ID)
    vulns_by_asset = {}

    for vuln in vulnerabilities:
        aid = vuln.get("aid")
        if aid not in vulns_by_asset:
            vulns_by_asset[aid] = []
        vulns_by_asset[aid].append(vuln)

    # Print vulnerabilities per asset
    for asset_id in asset_ids:
        if asset_id in vulns_by_asset:
            print(f"\n{'=' * 60}")
            print(f"Asset ID: {asset_id}")
            print(f"{'=' * 60}")

            vulns = vulns_by_asset[asset_id]
            print(f"Total vulnerabilities: {len(vulns)}\n")

            for idx, vuln in enumerate(vulns, 1):
                # Get CVE description and clean it
                cve_data = vuln.get("cve", {})
                description = cve_data.get("description", "N/A")

                # Replace newlines with spaces and trim to 30 characters
                description_clean = description.replace("\n", " ")[:120]

                print(f"  {idx}. CVE: {vuln.get('vulnerability_id')} Status: {vuln.get('status')} Risk Score: {vuln.get('risk_score')}  Exploitability: {vuln.get('exploitability')}")
                print(f"     Description: {description_clean}")

        else:
            print("No vulnerabilities found for this asset\n")


if __name__ == '__main__':
    sys.exit(main())
