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

    to_soup = True

    if to_soup:
        soup = BeautifulSoup(page.content, "html.parser")
        # content is html Doctype

        print("Soup contents:", len(soup.contents), "type ", type(soup.contents[0]),
              type(soup.contents[1]),
              type(soup.contents[2]),
              )

        table1 = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']=="DataTables_Table_0")

        print(table1)

        table2 = soup.find_all('table')

        print("t2", len(table2))

        my_divs = soup.find_all("div", class_="dl-desk-view")

        print(len(my_divs))

        for d in my_divs:
            print(d)

        sys.exit()

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
