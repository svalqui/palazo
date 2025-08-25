#!/usr/bin/env python
# https://github.com/sjkingo/python-freshdesk/tree/master


from freshdesk.api import API

from os import path

import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def main():

    my_api_key = input("My Api Key: ")

    my_fd = API('dhdnectar.freshdesk.com', my_api_key)

    # my_t = my_fd.tickets.get_ticket(224658)
    # print(my_t)
    # print(my_t.id, my_t.group_id, my_t.status)
    # print(dir(my_t))


    for t in my_fd.tickets.list_tickets():
        #print(dir(t))
        print(t)
        print(t.id, t.group_id, t.status)
        print()

        print(t, t.status)
        print()
        a = input()

    print("====")



if __name__ == '__main__':
    sys.exit(main())
