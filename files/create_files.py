import datetime
import time
while True:
    text_dt = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    file_name = text_dt + ".txt"
    file = open(file_name, "w")
    file.write(text_dt)
    file.close()
    time.sleep(60)
