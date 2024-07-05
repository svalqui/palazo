# Copyright 2019-2024 by Sergio Valqui. All rights reserved.
import json

import bs4.element
import requests
from bs4 import BeautifulSoup
import sys

from os import path
import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

from tools.util_obj import print_structure_det


def main():
    my_url = input("URL: ")
    page = requests.get(my_url)

    to_soup = False

    if to_soup:
        soup = BeautifulSoup(page.content, "html.parser")
        # content is html Doctype

        print("Soup contents:", len(soup.contents))
        print(soup.getText())
        for c in soup.contents:
            print(type(c), c.name)
            print()
            if isinstance(c, bs4.element.Tag):

                for index, descent in enumerate(c.descendants):
                    print("Type", type(descent), descent.name)
                    print(descent)
                    print(">>>>>>>>>>>")
                    print()
                    if index == 1 :
                        break
            else:
                print("No Tag", "Type", type(c))

        print("Looking for tables")
        print("Classes of each table")
        for table in soup.find_all('table'):
            print(table.get("class"))


        tables = soup.findAll("table")
        for table in tables:
            if table.findParent("table") is None:
                print(str(table))

        print(soup.prettify())



    else:
        data = page.json()
        print(json.dumps(data, sort_keys=True, indent=2))


if __name__ == '__main__':
    sys.exit(main())
