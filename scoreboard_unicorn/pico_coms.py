# PicoComs for Pimoroni MicroPython (Cosmic Unicorn). GIVEN: students don't edit this.
# Same job and same functions as pico_lib/pico_coms.py (the CircuitPython one).
#
# Reads WIFI_SSID, WIFI_PASSWORD and SERVER_URL from settings.py on the board.
#
#   from pico_coms import PicoComs
#   coms = PicoComs(name="scoreboard")
#   coms.connect()
#   coms.send("ball", {"seen": True})   # True if the server got it
#   data = coms.get("referee")          # dict, {} if nothing sent yet, None if unreachable
#   coms.age / coms.ip / coms.last_error / coms.last_status

import time

import network

try:
    import urequests as requests
except ImportError:
    import requests

import settings


class PicoComs:
    def __init__(self, name=None, server_url=None, ssid=None, password=None, timeout=2):
        self.name = name
        self.server_url = (server_url or settings.SERVER_URL).rstrip("/")
        self.ssid = ssid or settings.WIFI_SSID
        self.password = password if password is not None else settings.WIFI_PASSWORD
        self.timeout = timeout
        self.age = None          # age in seconds of the data from the last get()
        self.last_error = None   # text of the last failure, None after a success
        self.last_status = None  # HTTP status of the last reply, e.g. 200 or 403
        self.wlan = network.WLAN(network.STA_IF)

    @property
    def connected(self):
        return self.wlan.isconnected()

    @property
    def ip(self):
        return self.wlan.ifconfig()[0] if self.wlan.isconnected() else None

    def connect(self, attempts=None, retry_delay=3):
        """Join the Wi-Fi. attempts=None keeps trying forever. True once connected."""
        self.wlan.active(True)
        try:
            self.wlan.config(pm=0xA11140)  # stop the Wi-Fi dozing off (causes multi-second stalls)
        except (ValueError, OSError):
            pass
        tries = 0
        while not self.wlan.isconnected():
            if attempts is not None and tries >= attempts:
                return False
            tries += 1
            print("PicoComs: connecting to", self.ssid)
            try:
                self.wlan.connect(self.ssid, self.password)
            except OSError as e:
                self.last_error = "wifi: " + str(e)
            started = time.ticks_ms()
            while not self.wlan.isconnected() and time.ticks_diff(time.ticks_ms(), started) < 15000:
                time.sleep(0.2)
            if not self.wlan.isconnected():
                print("PicoComs: not joined yet (check the Wi-Fi name and password in settings.py)")
                time.sleep(retry_delay)
        print("PicoComs: connected, IP", self.ip)
        return True

    def announce(self, name):
        """Print this board's IP address in big letters for the students."""
        line = "=" * 46
        print("\n" + line)
        print("  This board (" + name + ") has the IP address:")
        print("\n      " + str(self.ip) + "\n")
        print("  Write it down and give it to the Server person.")
        print("  The server will be at:", self.server_url)
        print(line + "\n")

    def send(self, channel, data):
        """Send any JSON-able value to a channel on the server."""
        return self._request("POST", channel, data) is not None

    def get(self, channel):
        """Fetch the latest value on a channel. {} if nothing sent yet,
        None if the server can't be reached (see last_error). Sets self.age."""
        reply = self._request("GET", channel)
        if reply is None:
            self.age = None
            return None
        self.age = reply.get("age")
        data = reply.get("data")
        return {} if data is None else data

    def _request(self, method, channel, data=None):
        try:
            if not self.wlan.isconnected() and not self.connect(attempts=1):
                return None
            url = self.server_url + "/data/" + channel
            headers = {"X-Pico-Name": self.name} if self.name else {}
            kwargs = {"headers": headers}
            if data is not None:
                kwargs["json"] = data
            try:
                response = requests.request(method, url, timeout=self.timeout, **kwargs)
            except TypeError:  # older firmware without a timeout option
                response = requests.request(method, url, **kwargs)
            try:
                self.last_status = response.status_code
                if response.status_code != 200:
                    raise OSError("HTTP " + str(response.status_code))
                reply = response.json()
            finally:
                response.close()
            self.last_error = None
            return reply
        except Exception as e:  # network errors must never crash the caller
            if not str(e).startswith("HTTP "):
                self.last_status = None
            self.last_error = str(e)
            return None
