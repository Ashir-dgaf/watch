"""
MIT License

Copyright (c) 2021-2023 MShawon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from ast import Return
import io
import json
import logging
from os import access
import random,itertools
from tkinter.messagebox import RETRY
from bs4 import BeautifulSoup
import re
import textwrap
from concurrent.futures import ThreadPoolExecutor, wait
from time import gmtime, sleep, strftime
from time import time as tims

import psutil
from fake_headers import Headers, browsers
from faker import Faker
from requests.exceptions import RequestException
from tabulate import tabulate
from undetected_chromedriver.patcher import Patcher

from youtubeviewer import website
from youtubeviewer.basics import *
from youtubeviewer.config import create_config
from youtubeviewer.database import *
from youtubeviewer.download_driver import *
from youtubeviewer.load_files import *
from youtubeviewer.proxies import *


log = logging.getLogger('werkzeug')
log.disabled = True

SCRIPT_VERSION = '1.8.0'

print(bcolors.OKGREEN + """

Yb  dP  dP"Yb  88   88 888888 88   88 88""Yb 888888
 YbdP  dP   Yb 88   88   88   88   88 88__dP 88__
  8P   Yb   dP Y8   8P   88   Y8   8P 88""Yb 88""
 dP     YbodP  `YbodP'   88   `YbodP' 88oodP 888888

                        Yb    dP 88 888888 Yb        dP 888888 88""Yb
                         Yb  dP  88 88__    Yb  db  dP  88__   88__dP
                          YbdP   88 88""     YbdPYbdP   88""   88"Yb
                           YP    88 888888    YP  YP    888888 88  Yb
""" + bcolors.ENDC)

print(bcolors.OKCYAN + """
           [ GitHub : https://github.com/MShawon/YouTube-Viewer ]
""" + bcolors.ENDC)

print(bcolors.WARNING + f"""
+{'-'*26} Version: {SCRIPT_VERSION} {'-'*26}+
""" + bcolors.ENDC)

proxy = None
status = None
start_time = None
cancel_all = False

urls = []
queries = []
suggested = []

hash_urls = None
hash_queries = None
hash_config = None

driver_dict = {}
duration_dict = {}
checked = {}
summary = {}
video_statistics = {}
view = []
bad_proxies = []
used_proxies = []
temp_folders = []
console = []
dick = []

threads = 0
views = 100

fake = Faker()
cwd = os.getcwd()
patched_drivers = os.path.join(cwd, 'patched_drivers')
config_path = os.path.join(cwd, 'config.json')
driver_identifier = os.path.join(cwd, 'patched_drivers', 'chromedriver')

DATABASE = os.path.join(cwd, 'database.db')
DATABASE_BACKUP = os.path.join(cwd, 'database_backup.db')

animation = ["⢿", "⣻", "⣽", "⣾", "⣷", "⣯", "⣟", "⡿"]
headers_1 = ['Worker', 'Video Title', 'Watch / Actual Duration']
headers_2 = ['Index', 'Video Title', 'Views']

width = 0
viewports = ['1920,1080']

referers = ['https://search.yahoo.com/', 'https://duckduckgo.com/', 'https://www.google.com/',
            'https://www.bing.com/', 'https://t.co/', '']

referers = choices(referers, k=len(referers)*3)

website.console = console
website.database = DATABASE


def monkey_patch_exe(self):
    linect = 0
    replacement = self.gen_random_cdc()
    replacement = f"  var key = '${replacement.decode()}_';\n".encode()
    with io.open(self.executable_path, "r+b") as fh:
        for line in iter(lambda: fh.readline(), b""):
            if b"var key = " in line:
                fh.seek(-len(line), 1)
                fh.write(replacement)
                linect += 1
        return linect


Patcher.patch_exe = monkey_patch_exe


def timestamp():
    global date_fmt
    date_fmt = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    return bcolors.OKGREEN + f'[{date_fmt}] | ' + bcolors.OKCYAN + f'{cpu_usage} | '


def clean_exe_temp(folder):
    temp_name = None
    if hasattr(sys, '_MEIPASS'):
        temp_name = sys._MEIPASS.split('\\')[-1]
    else:
        if sys.version_info.minor < 7 or sys.version_info.minor > 11:
            print(
                f'Your current python version is not compatible : {sys.version}')
            print(f'Install Python version between 3.7.x to 3.11.x to run this script')
            input("")
            sys.exit()

    for f in glob(os.path.join('temp', folder, '*')):
        if temp_name not in f:
            shutil.rmtree(f, ignore_errors=True)


def update_chrome_version():
    link = 'https://gist.githubusercontent.com/MShawon/29e185038f22e6ac5eac822a1e422e9d/raw/versions.txt'

    output = requests.get(link, timeout=60).text
    chrome_versions = output.split('\n')

    browsers.chrome_ver = chrome_versions


def check_update():
    api_url = 'https://api.github.com/repos/MShawon/YouTube-Viewer/releases/latest'
    try:
        response = requests.get(api_url, timeout=30)

        RELEASE_VERSION = response.json()['tag_name']

        if RELEASE_VERSION > SCRIPT_VERSION:
            print(bcolors.OKCYAN + '#'*100 + bcolors.ENDC)
            print(bcolors.OKCYAN + 'Update Available!!! ' +
                  f'YouTube Viewer version {SCRIPT_VERSION} needs to update to {RELEASE_VERSION} version.' + bcolors.ENDC)

            try:
                notes = response.json()['body'].split(
                    'SHA256')[0].split('\r\n')
                for note in notes:
                    if note:
                        print(bcolors.HEADER + note + bcolors.ENDC)
            except Exception:
                pass
            print(bcolors.OKCYAN + '#'*100 + '\n' + bcolors.ENDC)
    except Exception:
        pass


def create_html(text_dict):
    if len(console) > 250:
        console.pop()

    date = f'<span style="color:#23d18b"> [{date_fmt}] | </span>'
    cpu = f'<span style="color:#29b2d3"> {cpu_usage} | </span>'
    str_fmt = ''.join(
        [f'<span style="color:{key}"> {value} </span>' for key, value in text_dict.items()])
    html = date + cpu + str_fmt

    console.insert(0, html)


def detect_file_change():
    global hash_urls, hash_queries, urls, queries

    if hash_urls != get_hash("urls.txt"):
        hash_urls = get_hash("urls.txt")
        urls = load_url()
        suggested.clear()

    if hash_queries != get_hash("search.txt"):
        hash_queries = get_hash("search.txt")
        queries = load_search()
        suggested.clear()


def direct_or_search(position):
    keyword = None
    video_title = None
    if position % 2:
        try:
            method = 1
            url = choice(urls)
            if 'music.youtube.com' in url:
                youtube = 'Music'
            else:
                youtube = 'Video'
        except IndexError:
            raise Exception("Your urls.txt is empty!")

    else:
        try:
            method = 2
            query = choice(queries)
            keyword = query[0]
            video_title = query[1]
            url = "https://www.youtube.com"
            youtube = 'Video'
        except IndexError:
            try:
                youtube = 'Music'
                url = choice(urls)
                if 'music.youtube.com' not in url:
                    raise Exception
            except Exception:
                raise Exception("Your search.txt is empty!")

    return url, method, youtube, keyword, video_title


def features(driver):
    if bandwidth:
        save_bandwidth(driver)

    bypass_popup(driver)

    bypass_other_popup(driver)

    play_video(driver)

    change_playback_speed(driver, playback_speed)


def update_view_count(position):
    view.append(position)
    view_count = len(view)
    print(timestamp() + bcolors.OKCYAN +
          f'Worker {position} | View added : {view_count}' + bcolors.ENDC)

    create_html({"#29b2d3": f'Worker {position} | View added : {view_count}'})

    if database:
        try:
            update_database(
                database=DATABASE, threads=max_threads)
        except Exception:
            pass


def set_referer(position, url, method, driver):
    referer = choice(referers)
    if referer:
        if method == 2 and 't.co/' in referer:
            driver.get(url)
        else:
            if 'search.yahoo.com' in referer:
                driver.get('https://duckduckgo.com/')
                driver.execute_script(
                    "window.history.pushState('page2', 'Title', arguments[0]);", referer)
            else:
                driver.get(referer)

            driver.execute_script(
                "window.location.href = '{}';".format(url))

        print(timestamp() + bcolors.OKBLUE +
              f"Worker {position} | Referer used : {referer}" + bcolors.ENDC)

        create_html(
            {"#3b8eea": f"Worker {position} | Referer used : {referer}"})

    else:
        driver.get(url)


def try_clicking(driver, css_selector, max_attempts=2):
    attempts = 0
    while attempts < max_attempts:
        try:
            play_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, css_selector))).click()
            return True
        except Exception as e:
            print("Attempt to click failed: ")
            attempts += 1

    return False

def youtube_normal(driver,url):
    driver.get("https://www.w3schools.com/html/tryit.asp?filename=tryhtml5_video")

    FLAG = True
    
    try:
        with open('LINK.txt', 'r') as file:
            data = file.read().replace('\n', '\\n')
        js_code = f"""
        var codeMirrorElement = document.querySelector('.CodeMirror').CodeMirror;
        codeMirrorElement.setValue('{data}');
        """

        # Execute the JavaScript code
        driver.execute_script(js_code)
        

        time.sleep(3)
        button_id = 'runbtn'
        js_code = f"""
        document.getElementById('{button_id}').click();
        """

        # Execute the JavaScript code
        # driver.execute_script(js_code)
        time.sleep(10)
        click_count = 0
        index = 0
        driver.execute_script('document.body.style.zoom="40%"')
        
        
        time.sleep(3600)
    except Exception as e:
        print(e)
        return 0
        
    






def spoof_timezone_geolocation(proxy_type, proxy, driver):
    try:
        proxy_dict = {
            "http": f"{proxy_type}://{proxy}",
                    "https": f"{proxy_type}://{proxy}",
        }
        resp = requests.get(
            "http://ip-api.com/json", proxies=proxy_dict, timeout=30)

        if resp.status_code == 200:
            location = resp.json()
            tz_params = {'timezoneId': location['timezone']}
            latlng_params = {
                "latitude": location['lat'],
                "longitude": location['lon'],
                "accuracy": randint(20, 100)
            }
            info = f"ip-api.com | Lat : {location['lat']} | Lon : {location['lon']} | TZ: {location['timezone']}"
        else:
            raise RequestException

    except RequestException:
        location = fake.location_on_land()
        tz_params = {'timezoneId': location[-1]}
        latlng_params = {
            "latitude": location[0],
            "longitude": location[1],
            "accuracy": randint(20, 100)
        }
        info = f"Random | Lat : {location[0]} | Lon : {location[1]} | TZ: {location[-1]}"

    try:
        driver.execute_cdp_cmd('Emulation.setTimezoneOverride', tz_params)

        driver.execute_cdp_cmd(
            "Emulation.setGeolocationOverride", latlng_params)

    except WebDriverException:
        pass

    return info



def windows_kill_drivers():
    for process in constructor.Win32_Process(["CommandLine", "ProcessId"]):
        try:
            if 'UserAgentClientHint' in process.CommandLine:
                print(f'Killing PID : {process.ProcessId}', end="\r")
                subprocess.Popen(['taskkill', '/F', '/PID', f'{process.ProcessId}'],
                                 stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
        except Exception:
            pass
    print('\n')


def quit_driver(driver, data_dir):
    if driver and driver in driver_dict:
        driver.quit()
        if data_dir in temp_folders:
            temp_folders.remove(data_dir)

    proxy_folder = driver_dict.pop(driver, None)
    if proxy_folder:
        shutil.rmtree(proxy_folder, ignore_errors=True)

    status = 400
    return status


def main_viewer(proxy_type, proxy, position):
    global width, viewports
    driver = None
    data_dir = None

    if cancel_all:
        raise KeyboardInterrupt

    try:
        detect_file_change()

        checked[position] = None

        header = Headers(
            browser="chrome",
            os=osname,
            headers=False
        ).generate()
        agent = header['User-Agent']

        # url, method, youtube, keyword, video_title = direct_or_search(position)

        if category == 'r' and proxy_api:
            for _ in range(20):
                proxy = choice(proxies_from_api)
                if proxy not in used_proxies:
                    break
            used_proxies.append(proxy)

        # status = check_proxy(category, agent, proxy, proxy_type)

        # if status != 200:
        #     raise RequestException(status)

        try:
            print(timestamp() + bcolors.OKBLUE + f"Worker {position} | " + bcolors.OKGREEN +
                  f"{proxy} | {proxy_type.upper()} | Good Proxy | Opening a new driver..." + bcolors.ENDC)

            create_html({"#3b8eea": f"Worker {position} | ",
                        "#23d18b": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | Good Proxy | Opening a new driver..."})

            while proxy in bad_proxies:
                bad_proxies.remove(proxy)
                sleep(1)

            patched_driver = os.path.join(
                patched_drivers, f'chromedriver_{position%threads}{exe_name}')

            try:
                Patcher(executable_path=patched_driver).patch_exe()
            except Exception:
                pass

            proxy_folder = os.path.join(
                cwd, 'extension', f'proxy_auth_{position}')

            factor = int(threads/(0.1*threads + 1))
            sleep_time = int((str(position)[-1])) * factor
            sleep(sleep_time)
            if cancel_all:
                raise KeyboardInterrupt
            try:
                account = random.choice(dick)

                driver ,status= get_driver(background, viewports, agent, auth_required,
                                    patched_driver, proxy, proxy_type, proxy_folder,account)
                if not status :
                    driver.quit()
                    dick.remove(account)
                    
            except Exception as e:
                print(f"ERROR AT LOGIN {e}")
                return

            driver_dict[driver] = proxy_folder

            data_dir = driver.capabilities['chrome']['userDataDir']
            temp_folders.append(data_dir)

            sleep(2)

            info = spoof_timezone_geolocation(proxy_type, proxy, driver)

            isdetected = driver.execute_script('return navigator.webdriver')

            print(timestamp() + bcolors.OKBLUE + f"Worker {position} | " + bcolors.OKGREEN +
                  f"{proxy} | {proxy_type.upper()} | " + bcolors.OKCYAN + f"{info} | Detected? : {isdetected}" + bcolors.ENDC)

            create_html({"#3b8eea": f"Worker {position} | ",
                        "#23d18b": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | ", "#29b2d3": f"{info} | Detected? : {isdetected}"})

            if width == 0:
                width = driver.execute_script('return screen.width')
                height = driver.execute_script('return screen.height')
                print(f'Display resolution : {width}x{height}')
                viewports = [i for i in viewports if int(i[:4]) <= width]

            # set_referer(position, url, '1', driver)

            # url = "https://facboowatchtimer.blogspot.com/2023/10/timer-videos.html"
            with open('LINK.txt', 'r') as f:
                url = f.read().strip()
            dick.remove(account)
            try:
                view_stat = youtube_normal(driver, url)
                dick.extend([account])
            except Exception as e:
                print(f'ERROR HERE{e}')
                dick.extend([account])

            
            status = quit_driver(driver=driver, data_dir=data_dir)

        except Exception as e:
            status = quit_driver(driver=driver, data_dir=data_dir)

            print(timestamp() + bcolors.FAIL +
                  f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}" + bcolors.ENDC)

            create_html(
                {"#f14c4c": f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}"})

    except RequestException:
        print(timestamp() + bcolors.OKBLUE + f"Worker {position} | " +
              bcolors.FAIL + f"{proxy} | {proxy_type.upper()} | Bad proxy " + bcolors.ENDC)

        create_html({"#3b8eea": f"Worker {position} | ",
                     "#f14c4c": f"{proxy.split('@')[-1]} | {proxy_type.upper()} | Bad proxy "})

        checked[position] = proxy_type
        bad_proxies.append(proxy)

    except Exception as e:
        print(timestamp() + bcolors.FAIL +
              f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}" + bcolors.ENDC)

        create_html(
            {"#f14c4c": f"Worker {position} | Line : {e.__traceback__.tb_lineno} | {type(e).__name__} | {e.args[0] if e.args else ''}"})


def get_proxy_list():
    if filename:
        if category == 'r':
            factor = max_threads if max_threads > 1000 else 1000
            proxy_list = [filename] * factor
        else:
            if proxy_api:
                proxy_list = scrape_api(filename)
            else:
                proxy_list = load_proxy(filename)

    else:
        proxy_list = gather_proxy()

    return proxy_list


def stop_server(immediate=False):
    if not immediate:
        print('Allowing a maximum of 15 minutes to finish all the running drivers...')
        for _ in range(180):
            sleep(5)
            if 'state=running' not in str(futures[1:-1]):
                break

    if api:
        for _ in range(10):
            response = requests.post(f'http://127.0.0.1:{port}/shutdown')
            if response.status_code == 200:
                print('Server shut down successfully!')
                break
            else:
                print(f'Server shut down error : {response.status_code}')
                sleep(3)


def clean_exit():
    print(timestamp() + bcolors.WARNING +
          'Cleaning up processes...' + bcolors.ENDC)
    create_html({"#f3f342": "Cleaning up processes..."})

    if osname == 'win':
        driver_dict.clear()
        windows_kill_drivers()
    else:
        for driver in list(driver_dict):
            quit_driver(driver=driver, data_dir=None)

    for folder in temp_folders:
        shutil.rmtree(folder, ignore_errors=True)


def cancel_pending_task(not_done):
    global cancel_all

    cancel_all = True
    for future in not_done:
        _ = future.cancel()

    clean_exit()

    stop_server(immediate=True)
    _ = wait(not_done, timeout=None)

    clean_exit()


def view_video(position):
    if position == 0:
        if api:
            website.start_server(host=host, port=port)

    elif position == total_proxies - 1:
        stop_server(immediate=False)
        clean_exit()

    else:
        sleep(2)
        proxy = proxy_list[position]

        if proxy_type:
            main_viewer(proxy_type, proxy, position)
        elif '|' in proxy:
            splitted = proxy.split('|')
            main_viewer(splitted[-1], splitted[0], position)
        else:
            main_viewer('http', proxy, position)
            if checked[position] == 'http':
                main_viewer('socks4', proxy, position)
            if checked[position] == 'socks4':
                main_viewer('socks5', proxy, position)


def main():
    global cancel_all, proxy_list, total_proxies, proxies_from_api, threads, hash_config, futures, cpu_usage

    cancel_all = False
    start_time = tims()
    hash_config = get_hash(config_path)

    proxy_list = get_proxy_list()
    if category != 'r':
        print(bcolors.OKCYAN +
              f'Total proxies : {len(proxy_list)}' + bcolors.ENDC)

    proxy_list = [x for x in proxy_list if x not in bad_proxies]
    if len(proxy_list) == 0:
        bad_proxies.clear()
        proxy_list = get_proxy_list()
    if proxy_list[0] != 'dummy':
        proxy_list.insert(0, 'dummy')
    if proxy_list[-1] != 'dummy':
        proxy_list.append('dummy')
    total_proxies = len(proxy_list)

    if category == 'r' and proxy_api:
        proxies_from_api = scrape_api(link=filename)

    threads = randint(min_threads, max_threads)
    if api:
        threads += 1

    loop = 0
    pool_number = list(range(total_proxies))

    if os.path.exists('accounts.json'):
        with open('accounts.json', 'r') as json_file:
            accounts_db = json.load(json_file)
    total_accounts = len(accounts_db)
    print('Total Account', total_accounts)
    for account in accounts_db:
        dick.extend([account])
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(view_video, position)
                for position in pool_number]

        done, not_done = wait(futures, timeout=0)
        try:
            while not_done:
                freshly_done, not_done = wait(not_done, timeout=1)
                done |= freshly_done

                loop += 1
                for _ in range(70):
                    cpu = str(psutil.cpu_percent(0.2))
                    cpu_usage = cpu + '%' + ' ' * \
                        (5-len(cpu)) if cpu != '0.0' else cpu_usage

                if loop % 40 == 0:
                    print(tabulate(video_statistics.items(),
                        headers=headers_2, showindex=True, tablefmt="pretty"))

                if category == 'r' and proxy_api:
                    proxies_from_api = scrape_api(link=filename)

                if len(view) >= views:
                    print(timestamp() + bcolors.WARNING +
                        f'Amount of views added : {views} | Stopping program...' + bcolors.ENDC)
                    create_html(
                        {"#f3f342": f'Amount of views added : {views} | Stopping program...'})

                    cancel_pending_task(not_done=not_done)
                    break

                elif hash_config != get_hash(config_path):
                    hash_config = get_hash(config_path)
                    print(timestamp() + bcolors.WARNING +
                        'Modified config.json will be in effect soon...' + bcolors.ENDC)
                    create_html(
                        {"#f3f342": 'Modified config.json will be in effect soon...'})

                    cancel_pending_task(not_done=not_done)
                    break

                elif refresh != 0 and category != 'r':

                    if (tims() - start_time) > refresh*60:
                        start_time = tims()

                        proxy_list_new = get_proxy_list()
                        proxy_list_new = [
                            x for x in proxy_list_new if x not in bad_proxies]

                        proxy_list_old = [
                            x for x in proxy_list[1:-1] if x not in bad_proxies]

                        if sorted(proxy_list_new) != sorted(proxy_list_old):
                            print(timestamp() + bcolors.WARNING +
                                f'Refresh {refresh} minute triggered. Proxies will be reloaded soon...' + bcolors.ENDC)
                            create_html(
                                {"#f3f342": f'Refresh {refresh} minute triggered. Proxies will be reloaded soon...'})

                            cancel_pending_task(not_done=not_done)
                            break

        except KeyboardInterrupt:
            print(timestamp() + bcolors.WARNING +
                'Hold on!!! Allow me a moment to close all the running drivers.' + bcolors.ENDC)
            create_html(
                {"#f3f342": 'Hold on!!! Allow me a moment to close all the running drivers.'})

            cancel_pending_task(not_done=not_done)
            raise KeyboardInterrupt


if __name__ == '__main__':

    clean_exe_temp(folder='youtube_viewer')
    date_fmt = datetime.now().strftime("%d-%b-%Y %H:%M:%S")
    cpu_usage = str(psutil.cpu_percent(1))
    current_directory = os.getcwd()
    opx = download_driver(current_directory)
    osname, exe_name = "win" , ".exe"
    create_database(database=DATABASE, database_backup=DATABASE_BACKUP)

    if osname == 'win':
        import wmi
        constructor = wmi.WMI()

    urls = load_url()
    queries = load_search()

    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8-sig') as openfile:
            config = json.load(openfile)

    else:
        create_config(config_path=config_path)

    hash_urls = get_hash("urls.txt")
    hash_queries = get_hash("search.txt")
    hash_config = get_hash(config_path)

    while len(view) < views:
        try:
            with open(config_path, 'r', encoding='utf-8-sig') as openfile:
                config = json.load(openfile)

            if cancel_all:
                print(json.dumps(config, indent=4))
            api = config["http_api"]["enabled"]
            host = config["http_api"]["host"]
            port = config["http_api"]["port"]
            database = config["database"]
            views = config["views"]
            minimum = config["minimum"] / 100
            maximum = config["maximum"] / 100
            category = config["proxy"]["category"]
            proxy_type = config["proxy"]["proxy_type"]
            filename = config["proxy"]["filename"]
            auth_required = config["proxy"]["authentication"]
            proxy_api = config["proxy"]["proxy_api"]
            refresh = config["proxy"]["refresh"]
            background = config["background"]
            bandwidth = config["bandwidth"]
            playback_speed = config["playback_speed"]
            max_threads = config["max_threads"]
            min_threads = config["min_threads"]

            if minimum >= maximum:
                minimum = maximum - 5

            if min_threads >= max_threads:
                max_threads = min_threads

            if auth_required and background:
                print(bcolors.FAIL +
                      "Premium proxy needs extension to work. Chrome doesn't support extension in Headless mode." + bcolors.ENDC)
                input(bcolors.WARNING +
                      f"Either use proxy without username & password or disable headless mode " + bcolors.ENDC)
                sys.exit()

            copy_drivers(cwd=cwd, patched_drivers=patched_drivers,
                         exe=exe_name, total=max_threads)

            main()
        except KeyboardInterrupt:
            sys.exit()
