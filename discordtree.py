import requests
import random
from capmonster_python import ImageToTextTask
from datetime import datetime
import os
from colorama import Fore
import json

GREEN = Fore.GREEN
BLUE = Fore.BLUE
YELLOW = Fore.YELLOW
RED = Fore.RED
RESET = Fore.RESET
MAGENTA = Fore.MAGENTA

date_and_time = datetime.now()
time = date_and_time.strftime('%H:%M:%S')

with open('info.json', 'r') as file:
    data = json.load(file)

captchakey = data['captchamonster_key']
vote_id = data['vote_id']

def download_and_solve_captcha(api_key, captcha_image_url, proxy, session):
    date_and_time = datetime.now()
    time = date_and_time.strftime('%H:%M:%S')
    local_image_path = 'captcha.png'
    if os.path.exists(local_image_path):
        os.remove(local_image_path)

    try:
        ip, port = proxy.split(":")
        proxy = f"http://{ip}:{port}"
        proxies = {
            "http": proxy,
        }

        # Download the captcha image
        response = session.get(captcha_image_url, proxies=proxies)
        with open(local_image_path, 'wb') as f:
            f.write(response.content)

        capmonster = ImageToTextTask(api_key)
        task_id = capmonster.create_task(image_path=local_image_path)
        result = capmonster.join_task_result(task_id)

        solution = result.get("text")
        solution = solution.replace("o", "0")
        solution = solution.upper()
        print(f"[{BLUE}{time}{RESET}] [{MAGENTA}CAPTCHA FOUND{RESET}] [{YELLOW}{solution}{RESET}]")
        return solution

    except Exception as e:
        print(e)
        return None

def main():
    capmonster_api_key = captchakey

    captcha_image_url = "https://discordtree.com/captcha.png"

    proxies_file = open('proxies.txt', 'r')
    proxies_list = [line.strip() for line in proxies_file.readlines()]
    proxies_file.close()
    random.shuffle(proxies_list)

    session = requests.Session()

    for proxy in proxies_list:
        try:
            captcha_solution = download_and_solve_captcha(capmonster_api_key, captcha_image_url, proxy, session)

            if captcha_solution:
                form_url = f"https://discordtree.com/vote-{vote_id}"

                form_payload = {
                    "id": vote_id,
                    "captcha": captcha_solution,
                    "submit": ""
                }

                response = session.post(form_url, data=form_payload, proxies=session.proxies)
                if response.status_code == 200 or 302:
                    print(f"[{BLUE}{time}{RESET}] [{GREEN}SUCCESS{RESET}] [{YELLOW}Added vote!{RESET}]")
                else:
                    print(f"[{BLUE}{time}{RESET}] [{RED}ERROR{RESET}] [{YELLOW}Form submission failed. Status code: {response.status_code}{RESET}]")
            else:
                print(f"[{BLUE}{time}{RESET}] [{RED}ERROR{RESET}] [{YELLOW}Failed to get captcha solution.{RESET}]")
        except Exception as e:
            print(e)
            continue
        finally:
            session.close()


if __name__ == "__main__":
    main()
