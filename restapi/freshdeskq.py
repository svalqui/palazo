#!/usr/bin/env python
# https://github.com/sjkingo/python-freshdesk/tree/master


from freshdesk.api import API

from os import path

import sys
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )

def main():

    my_api_key = input("My Api Key: ")

    my_fd = API('dhdnectar.freshdesk.com', my_api_key)


    a_ticket = my_fd.tickets.get_ticket()
    print(a_ticket)
    print(dir(a_ticket))
    print("id", a_ticket.id)
    print("sub",a_ticket.subject)
    print("responder", a_ticket.responder_id)
    print("requester_id", a_ticket.requester_id)
    print("group", a_ticket.group_id)
    print("tags", a_ticket.tags)
    print("type", a_ticket.type)
    print("status", a_ticket.status)
    print("cc-emails", a_ticket.cc_emails)
    print("to-emails", a_ticket.to_emails)
    print("email-conf-id", a_ticket.email_config_id)
    print("support-email", a_ticket.support_email)
    print("association-type", a_ticket.association_type)
    print("custom-fields", a_ticket.custom_fields)
    print()


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
