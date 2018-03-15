def IsAuMrkO(self):

    opened = False


#  https://www.asx.com.au/

    import requests
    from bs4 import BeautifulSoup

    # Collect and parse page
    page = requests.get('https://www.asx.com.au')
    soup = BeautifulSoup(page.text, 'html.parser')

    return opened
