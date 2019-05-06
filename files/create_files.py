# Copyright 2019 by Sergio Valqui. All rights reserved.
import datetime
import time
while True:
    text_dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")
    file_name = text_dt + ".txt"
    file = open(file_name, "w")
    file.write(text_dt)
    file.close()
    print("Created ", file_name)
    time.sleep(60)
