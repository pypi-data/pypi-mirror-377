import time
import sys
import asyncio
import httpx
import struct
import base64
from urllib.parse import urlencode
from urllib.parse import urljoin

class LeaseError(Exception):
    """Raised when lease acquisition or renewal fails."""

class ChannelPub:
    _BASE_URL = "https://api.trickler.com/publish/"  # "private" class constant

    def __init__(self, channel_id, access_key, renew_interval=15):
        self._channel_id = channel_id
        self._access_key = access_key
        self._renew_interval = renew_interval  # seconds between renewal attempts
        self._correlation_id = None
        self._renewal_counter = 0
        self._client = httpx.AsyncClient(base_url=self._BASE_URL)
        self._running = False
        self._renewal_task = None
        #self._endian = "little" if sys.byteorder == "little" else "big"

    async def start(self):
        """
        Start the session: obtain lease and begin periodic renewal.
        Raises LeaseError if lease cannot be obtained.
        """
        # Only try if not already running
        if self._running:
            return
        response = await self._obtain_lease()
        if not self._correlation_id:
            raise LeaseError("Failed to obtain lease")
        self._running = True
        # Start periodic renewal in the background
        self._renewal_task = asyncio.create_task(self._periodic_renewal())

    async def send_value(self, value: float):
        """
        Public: Accepts a Python float (64-bit IEEE double), encodes to base64, and sends.
        Raises LeaseError if lease is not valid.
        """
        if not self._running or not self._correlation_id:
            raise LeaseError("Cannot send value: not started or lease expired")
        if not isinstance(value, float):
            raise TypeError("send_value accepts only a float (64-bit double)")
        # Convert float to bytes (8 bytes, IEEE 754), default little-endian
        fmt = "<d"
        #if self._endian == "little" else ">d"

        ts_millis = time.time_ns() // 1_000_000
        fmt = "<Qd" 
        #if endian == "little" else ">Qd"
        payload_bytes = struct.pack(fmt, ts_millis, float(value))        
        #byte_array = struct.pack(fmt, value)
        # Encode as base64 string
        b64_encoded = base64.b64encode(payload_bytes).decode("ascii")
                
        try:
            await self._send_value(b64_encoded)
        except httpx.HTTPStatusError as ex:
            if ex.response.status_code == httpx.codes.FORBIDDEN:
                # Lease has expired or is invalid
                self._running = False
                self._correlation_id = None
                raise LeaseError("Lease expired during send_value (403 Forbidden)")
            raise

    async def stop(self):
        """
        Public: End session and stop renewal.
        """
        self._running = False
        if self._renewal_task:
            self._renewal_task.cancel()
        if self._correlation_id:
            await self._end_session()
            self._correlation_id = None   

    async def _periodic_renewal(self):
        """
        Internal: Periodically renew lease every self._renew_interval seconds.
        Stops if renewal fails.
        """
        try:
            while self._running:
                await asyncio.sleep(self._renew_interval)
                response = await self._renew_lease()
                # If correlation_id is lost, this means lease failed or expired
                if not self._correlation_id:
                    # Transition to stopped state
                    self._running = False
                    self._log_information("Lease renewal failed, instance stopped.")
                    break
        except Exception as ex:
            self._running = False
            self._log_information(f"Renewal task stopped due to error: {ex}")            

    async def _obtain_lease(self):
        """
        Obtain a lease (session) from the channel.
        Sets correlation/session id from response headers for future use.
        """
        url = f"{self._channel_id}/lease"
        # Form data as a dictionary
        data = {
            "accessKey": self._access_key
        }
        # Send a POST request with form data
        response = await self._client.post(url, data=data)
        # Try to get the correlation/session id from header
        corr_id = response.headers.get("PublicationCorrelationID")
        if corr_id:
            self._correlation_id = corr_id
            # You might want to log or print here for debugging
        return response  # Optionally return for further inspection

    async def _renew_lease(self):
        """
        Renew the lease (session) with the server.
        Handles response codes and updates internal state.
        """
        url = f"{self._channel_id}/lease"
        data = {
            "accessKey": self._access_key,
            "correlationID": self._correlation_id
        }
        # PATCH is more rare; supported by httpx
        response = await self._client.patch(url, data=data)
        code = response.status_code
        if code == httpx.codes.OK:
            self._renewal_counter += 1
            # Lease renewed successfully
        elif code == httpx.codes.LOCKED:
            # Session already active elsewhere
            self._correlation_id = None
            self._log_information("Session lost on renewal.")
        elif code == httpx.codes.PRECONDITION_FAILED:
            # No quota left for renewal
            self._correlation_id = None
            self._log_information("Insufficient quota on renewal.")
        else:
            # All other errors are terminal
            self._correlation_id = None
            self._terminal_error("Failure renewing session")
            return
        return response

    async def _end_session(self):
        """
        End the session by sending a DELETE lease request.
        Checks for error codes and raises exceptions as needed.
        """
        url = urljoin(self._BASE_URL, f"{self._channel_id}/lease")
        data = {
            "accessKey": self._access_key,
            "correlationID": self._correlation_id
        }
        try:            
            # Encode the data as application/x-www-form-urlencoded
            content = urlencode(data)
            # Build the request manually
            request = httpx.Request(
                "DELETE",
                url,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                content=content,
            )
            response = await self._client.send(request)
        except Exception as ex:
            # Suppress any errors during HTTP call (not recommended for production)
            response = None

        if response:
            code = response.status_code
            if code == httpx.codes.OK or code == httpx.codes.NO_CONTENT:
                return
            elif code == httpx.codes.FORBIDDEN:
                raise Exception(response.reason_phrase)
            else:
                raise Exception(f"Unexpected status code: {code}, reason: {response.reason_phrase}")

    async def _send_value(self, encoded_payload):
        """
        Send a value update to the channel.
        Raises an error if not successful.
        """
        url = f"{self._channel_id}/updates"
        data = {
            "accessKey": self._access_key,
            "encodedPayload": encoded_payload,
            "correlationID": self._correlation_id
        }
        response = await self._client.post(url, data=data)
        code = response.status_code
        if code == httpx.codes.OK:
            return
        else:
            raise Exception(f"SendValue failed. StatusCode={code}")

    # Optional: simple logging helpers
    def _log_information(self, msg):
        print(f"[INFO] {msg}")

    def _terminal_error(self, msg):
        print(f"[ERROR] {msg}")