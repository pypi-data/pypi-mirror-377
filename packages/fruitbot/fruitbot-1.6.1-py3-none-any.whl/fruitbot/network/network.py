from ..crypto import Encryption
from ..configs import exceptions
from json import dumps, loads
from urllib3 import PoolManager
from urllib3.exceptions import TimeoutError
import logging


class Network:
    def __init__(self, passport, enc_version=None, base_url=None, time_out=None):
        self.crypto = Encryption(version=enc_version)
        self.http = PoolManager()
        self.time_out = time_out or 10
        self.base_url = base_url or "https://iran.fruitcraft.ir"
        self.headers = {"Accept-Encoding": "gzip",
                        "Connection": "Keep-Alive",
                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                        "Cookie": f"FRUITPASSPORT={passport};",
                        "Host": "iran.fruitcraft.ir",
                        "User-Agent": "Dalvik/2.1.0"
                        }

    def sendRequest(self, path: str, input: dict = {"client": "iOS"}, method: str = "POST", max_attempts: int = 5):
        url = f"{self.base_url}/{path}"
        data = f"edata={self.crypto.encrypt(dumps(input))}&version={self.crypto.version}" if method == "POST" else None

        for i in range(1, max_attempts+1):
            try:
                response = self.http.request(method=method,
                                             url=url,
                                             headers=self.headers,
                                             body=data,
                                             timeout=self.time_out)
                break
            except TimeoutError as e:
                logging.warning(f"{e} attempt {i}/{max_attempts}")
                if i == max_attempts:
                    raise e
                continue


        if response.status == 429:
            raise exceptions[429]()

        if response.headers.get("content-type", "").startswith("image/"):
            return response.data
        # Decode response data to UTF-8 and remove any BOM.
        response = response.data.decode("UTF-8").lstrip('\ufeff')
        if response.startswith("<!DOCTYPE"):
            raise exceptions[None]()
        try:
            response = loads(self.crypto.decrypt(response))
            if response.get('status'):
                return response["data"]
        except exceptions as e:
            pass
        try:
            error_code = response["data"]["code"]
            error_args = tuple(response["data"]["arguments"])
        except Exception as e:
            raise exceptions[None]()
        raise exceptions[error_code](error_args)

