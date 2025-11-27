import os
from falconpy import ExposureManagement

falcon = ExposureManagement(client_id=os.getenv("FALCON_CLIENT_ID"),
                            client_secret=os.getenv("FALCON_CLIENT_SECRET"),
                           )

response = falcon.query_external_assets_v2(offset=0,
                                           limit=10,
#                                           sort="string",
#                                           filter="string"
                                           )
print(response)