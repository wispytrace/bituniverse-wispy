import requests
import time

URL_IP = "http://154.215.142.112:8000/"


def send_req():

    try:

        update_res = requests.get(url=URL_IP+"api/update")
        
    except Exception as e:
        print(repr(e))



if __name__ == '__main__':
    
    count = 0
    while True:
        try:
            count += 1
            if count == 60000:
                update_res = requests.get(url=URL_IP+"api/clear_orders")
                count = 0
            else:
                update_res = requests.get(url=URL_IP+"api/update")
            time.sleep(1)
        except Exception as e:
            print(repr(e))
