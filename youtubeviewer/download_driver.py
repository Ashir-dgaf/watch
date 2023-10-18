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
import platform
import shutil
import subprocess
import sys
import requests
import time
from tqdm import tqdm
from colorama import Fore, init
from zipfile import ZipFile

from .colors import *

unique_links_dict = {}

# Initialize colorama
init()

# COLOURS VERIABLES
RE = Fore.RED
G = Fore.GREEN
C = Fore.CYAN
Y = Fore.YELLOW
B = Fore.BLUE
W = Fore.WHITE
M = Fore.MAGENTA
LR = Fore.LIGHTRED_EX
LG = Fore.LIGHTGREEN_EX
LC = Fore.LIGHTCYAN_EX
LB = Fore.LIGHTBLUE_EX
LY = Fore.LIGHTYELLOW_EX
LW = Fore.LIGHTWHITE_EX
LM = Fore.LIGHTMAGENTA_EX
R = Fore.RESET

def find_compatible_version(target_version,api_response,platform_arch):
    for version_data in api_response["versions"]:
        if version_data["version"].startswith(target_version):
            chromedriver_url = None

            
            for driver_entry in version_data["downloads"].get("chromedriver", []):
                if f"win{platform_arch}" in driver_entry["url"]:
                    chromedriver_url = driver_entry["url"]
                    break
            
            if chromedriver_url:
                return version_data, chromedriver_url
    
    return None, None

def get_chrome_version():
    try:
        if sys.platform.startswith('win'):
            command = 'reg query "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon" /v version'
        elif sys.platform.startswith('darwin'):
            command = '/Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version'
        else:
            command = 'google-chrome --version'

        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        version = result.decode().strip().split()[-1]
        return version
    except Exception as e:
        print(f"Error while getting Chrome version: {e}")
        return None

def get_system_architecture():
    try:
        arch, _ = platform.architecture()
        return int(arch[:2])
    except Exception as e:
        print(e)
        return 64

def download_chromedriver(version, arch,current_directory):
    opx = f"chromedriver-win{arch}"
    chromedriver_folder = f"{current_directory}/{opx}"
    chromedriver_file_path = f'{opx}/chromedriver.exe'
    delete_dir = f"{current_directory}/{opx}/chromedriver.exe"

    chromedriver_zip_url = f"https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/{version}/win64/{opx}.zip"

    try:
        response = requests.get(chromedriver_zip_url, stream=True)
        response.raise_for_status()

        os.makedirs(chromedriver_folder, exist_ok=True)
        total_size = int(response.headers.get('content-length', 0))
        
        if os.path.exists(f"{current_directory}/chromedriver.exe"):
            os.remove(f"{current_directory}/chromedriver.exe")
                
        with open(f'{chromedriver_folder}.zip', 'wb') as zip_file:
            with tqdm(total=total_size, unit='B', unit_scale=True, unit_divisor=1024, desc="Downloading Chromedriver") as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    zip_file.write(chunk)
                    pbar.update(len(chunk))
        
        with ZipFile(f'{chromedriver_folder}.zip', 'r') as zip_ref:
            zip_ref.extract(chromedriver_file_path, path=f"{current_directory}/")
        

        shutil.move(delete_dir, f'{current_directory}/chromedriver.exe')

        os.remove(f'{chromedriver_folder}.zip')
        shutil.rmtree(chromedriver_folder)

        print('Chromedriver downloaded successfully.')
        time.sleep(2)
        return True
    except requests.exceptions.RequestException:
        return False

def save_chrome_version(version,current_directory):
    with open(f"{current_directory}/version", "w") as f:
        f.write(version)

def load_saved_chrome_version(current_directory):
    if os.path.exists(f"{current_directory}/version"):
        with open(f"{current_directory}/version", "r") as f:
            return f.read().strip()
        
    return None

def download_driver(current_directory):
    if os.path.exists(f"{current_directory}/chromedriver.exe"):
        pass
    else:
        if os.path.exists(f"{current_directory}/version"):
            os.remove(current_directory+"/version")
        else: pass
    
    chrome_version = get_chrome_version()
    saved_chrome_version = load_saved_chrome_version(current_directory)
    system_architecture = get_system_architecture()
    
    
    if chrome_version:
        # print(f"{Y}Detected Chrome version: {chrome_version}{R}")
        if chrome_version != saved_chrome_version:
            print(f'{LB}Fetching Chromedriver v{chrome_version}{R}')
            if not download_chromedriver(chrome_version, system_architecture,current_directory):
                api_response = requests.get("https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json").json()
                strategies = [chrome_version, '.'.join(chrome_version.split('.')[:3]), '.'.join(chrome_version.split('.')[:2])]
                found_version, chromedriver_url = None, None

                for strategy in strategies:
                    found_version, chromedriver_url = find_compatible_version(strategy,api_response,system_architecture)
                    if found_version and chromedriver_url:
                        break
                if not found_version:
                    # Search for outdated versions
                    outdated_versions = ["115.0.5765.0", "116.0.5806.0"]  # Add more versions if needed
                    
                    for outdated_version in outdated_versions:
                        found_version, chromedriver_url = find_compatible_version(outdated_version,api_response,system_architecture)
                        if found_version and chromedriver_url:
                            break

                if found_version  and chromedriver_url:
                    found_version = found_version["version"]
                    print(f"{Y}Oops, Trying with {found_version}...{R}")
                    if not download_chromedriver(found_version, system_architecture,current_directory):
                        print('Chromedriver download failed for all attempts.')
                        
                        print(f"{LR}Couldn't download driver automatically. Please grab v{chrome_version} manually! , redirecting you to download page{R}")
                        try:
                            os.system('start https://chromedriver.chromium.org/downloads')
                        except Exception as e:
                            print(f'{Y}Failed to open webpage , here is the link download the latest driver from this url , https://chromedriver.chromium.org/downloads')
                            pass
                    else:
                        save_chrome_version(chrome_version,current_directory)
                else:
                    print("No matching Chrome driver version found.")
                
            else:
                save_chrome_version(chrome_version,current_directory)
                
        else:
            print('Chromedriver is up to date! Time for some smooth surfing.')
        
    else:
        save_chrome_version('0',current_directory)
        return check_update(current_directory)





CHROME = ['{8A69D345-D564-463c-AFF1-A69D9E530F96}',
          '{8237E44A-0054-442C-B6B6-EA0509993955}',
          '{401C381F-E0DE-4B85-8BD8-3F3F14FBDA57}',
          '{4ea16ac7-fd5a-47c3-875b-dbf4a2008c20}']




def copy_drivers(cwd, patched_drivers, exe, total):
    current = os.path.join(cwd, f'chromedriver{exe}')
    os.makedirs(patched_drivers, exist_ok=True)
    for i in range(total+1):
        try:
            destination = os.path.join(
                patched_drivers, f'chromedriver_{i}{exe}')
            shutil.copy(current, destination)
        except Exception:
            pass
