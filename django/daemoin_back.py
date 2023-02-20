import requests
import time

URL_IP = "http://103.42.182.82:8000/"


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
            count += 1
            if count >= 60000:
                update_res = requests.get(url=URL_IP+"api/clear_orders")
                count = 0
            elif count % 600 == 0:
                update_res = requests.get(url=URL_IP+"api/check_robots")
            else:
                update_res = requests.get(url=URL_IP+"api/update")
            time.sleep(0.5)

        except Exception as e:
            time.sleep(1)
            print(repr(e))
