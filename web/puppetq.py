# puppet query

import ssl
import urllib.request


def puppet_query(puppet_db_site, path_pem, path_key, path_cacert, data_urlencode):
    context = ssl.create_default_context()
    context.load_cert_chain(path_pem, path_key)
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
    response = opener.open(puppet_db_site)
    print(response.read())

# Reference
# https://stackoverflow.com/questions/1875052/using-client-certificates-with-urllib2#4464435
