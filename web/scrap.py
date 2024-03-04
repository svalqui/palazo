# Copyright 2019-2024 by Sergio Valqui. All rights reserved.
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
    soup = BeautifulSoup(page.content, "html.parser")
    # content is html Doctype
    print (len(soup.contents))
    print(soup.getText())
    for c in soup.contents:
        print(type(c), c.name)
        print()
        if isinstance(c,bs4.element.Tag):

            for index, descent in enumerate(c.descendants):
                print("Type", type(descent), descent.name)
                print(descent)
                print(">>>>>>>>>>>")
                print()
                if index == 10 :
                    break

if __name__ == '__main__':
    sys.exit(main())
