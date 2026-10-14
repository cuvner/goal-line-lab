# PicoComs - general purpose Wi-Fi comms for Pico W clients (CircuitPython)
#
# Copy this file to CIRCUITPY/lib/ on every Pico W.
# Needs in CIRCUITPY/lib: adafruit_requests.mpy, adafruit_connection_manager.mpy
# Reads WIFI_SSID, WIFI_PASSWORD and SERVER_URL from CIRCUITPY/settings.toml
#
# Usage:
#   from pico_coms import PicoComs
#   coms = PicoComs(name="huskylens")   # name shows up on the server dashboard
#   coms.connect()
#   coms.send("ball", {"seen": True, "x": 160})   # True if the server got it
#   data = coms.get("ball")                        # dict, or None if unreachable
#   coms.age                                       # seconds since "ball" was last sent

import os
import ssl
import time

import adafruit_requests
import socketpool
import wifi


class PicoComs:
    def __init__(self, name=None, server_url=None, ssid=None, password=None, timeout=2):
        self.name = name or os.getenv("DEVICE_NAME")
        self.server_url = (server_url or os.getenv("SERVER_URL")).rstrip("/")
        self.ssid = ssid or os.getenv("WIFI_SSID")
        self.password = password if password is not None else os.getenv("WIFI_PASSWORD")
        self.timeout = timeout
        self.age = None         # age in seconds of the data from the last get()
        self.last_error = None  # text of the last failure, None after a success
        self._session = None

    @property
    def connected(self):
        return wifi.radio.connected

    @property
    def ip(self):
        return str(wifi.radio.ipv4_address) if wifi.radio.connected else None

    def connect(self, attempts=None, retry_delay=3):
        """Join the Wi-Fi. attempts=None keeps trying forever.
        Returns True once connected."""
        tries = 0
        while not wifi.radio.connected:
            if attempts is not None and tries >= attempts:
                return False
            tries += 1
            try:
                print("PicoComs: connecting to", self.ssid)
                wifi.radio.connect(self.ssid, self.password)
            except (ConnectionError, OSError) as e:
                self.last_error = "wifi: " + str(e)
                print("PicoComs:", self.last_error)
                time.sleep(retry_delay)
        if self._session is None:
            pool = socketpool.SocketPool(wifi.radio)
            self._session = adafruit_requests.Session(pool, ssl.create_default_context())
            print("PicoComs: connected, IP", self.ip)
        return True

    def send(self, channel, data):
        """Send any JSON-able value to a channel on the server."""
        return self._request("POST", channel, data) is not None

    def get(self, channel):
        """Fetch the latest value on a channel.
        Returns {} if nothing has been sent to it yet, None if the server
        can't be reached (see last_error). Sets self.age."""
        reply = self._request("GET", channel)
        if reply is None:
            self.age = None
            return None
        self.age = reply.get("age")
        data = reply.get("data")
        return {} if data is None else data

    def _request(self, method, channel, data=None):
        try:
            if not wifi.radio.connected and not self.connect(attempts=1):
                return None
            url = self.server_url + "/data/" + channel
            headers = {"X-Pico-Name": self.name} if self.name else None
            with self._session.request(
                method, url, json=data, headers=headers, timeout=self.timeout
            ) as response:
                if response.status_code != 200:
                    raise OSError("HTTP " + str(response.status_code))
                reply = response.json()
            self.last_error = None
            return reply
        except Exception as e:  # network errors must never crash the caller
            self.last_error = str(e)
            return None
