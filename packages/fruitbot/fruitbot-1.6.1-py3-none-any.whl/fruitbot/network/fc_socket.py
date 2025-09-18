import socket
import json
from ..crypto import Encryption
from ..configs.configs import exceptions
import logging
from threading import Thread, Event
from time import time

crypto = Encryption(is_socket=True)
START_MARKER, END_MARKER = "__JSON__START__", "__JSON__END__"

class Socket:
    def __init__(self):
        self.user_id = None
        self.tribe_id = None
        self.avatar_id = 1  # default
        self.user_name = None
        self.sock = None
        self.connected = False
        self.will_reconnect = Event()
        self.handlers = {}
        self.start_time = time()

    def connect(self):
        self.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(("iranchat.fruitcraft.ir", 1337))
        self.connected = True
        if self.user_id:
            self._subscribe(f"user{self.user_id}")
        if self.tribe_id:
            self._subscribe(f"tribe{self.tribe_id}")

    def close(self, reconnect=True):
        if not self.sock:
            return

        if reconnect:
            self.will_reconnect.set()
        else:
            self.connected = False
        self.sock.close()

    def _subscribe(self, channel):
        if self.connected:
            message = f'__SUBSCRIBE__{crypto.encrypt(channel)}__ENDSUBSCRIBE__'
            self.sock.sendall(message.encode())

    def _unsubscribe(self, channel):
        # It doesn't work
        message = f'__UNSUBSCRIBE__{crypto.encrypt(channel)}__ENDUNSUBSCRIBE__'
        self.sock.sendall(message.encode())

    def _send_data(self, data):
        encrypted = crypto.encrypt(json.dumps(data, ensure_ascii=False))
        self.sock.sendall(f"{START_MARKER}{encrypted}{END_MARKER}".encode())

    def set_info(self, user_id=None, tribe_id=None, avatar_id=None, user_name=None):
        if tribe_id:
            self.tribe_id = tribe_id
            self._subscribe(f"tribe{tribe_id}")
        if user_id:
            self.user_id = user_id
            self._subscribe(f"user{user_id}")

        if avatar_id:
            self.avatar_id = avatar_id
        if user_name:
            self.user_name = user_name

    def unset_info(self, tribe=False):
        if tribe:
            self.tribe_id = None
            self.connect()
            Thread(target=self.receive_messages, args=[]).start()

    def send_tribe_message(self, text):
        if not self.tribe_id:
            raise exceptions[149]
        now = time()
        data = {
            "push_message_type": "chat",
            "id": int(now),
            "text": text,
            "avatar_id": self.avatar_id,
            "creationDate": int(now),
            "channel": f"tribe{self.tribe_id}",
            "timestamp": round((now - self.start_time) * 1000, 3),
            "sender": self.user_name,
            "messageType": 1
        }
        self._send_data(data)
        return data

    def add_handler(self, message_type, func):
        self.handlers[message_type] = func
        return func

    def _get_buffer_contents(self, raw_data):
        messages = []
        while END_MARKER in raw_data:
            msg, raw_data = raw_data.split(END_MARKER, 1)
            if START_MARKER in msg:
                messages.append(json.loads(crypto.decrypt(msg[15:])))
        return messages, raw_data

    def receive_messages(self):
        buffer = ""
        while True:
            try:
                data = self.sock.recv(4096).decode()
                if not data:
                    break

                buffer += data
                messages, buffer = self._get_buffer_contents(buffer)
                for msg in messages:
                    if msg.get("push_message_type") == "tribe_join":
                        self.tribe_id = msg["tribe"]["id"]
                        self._subscribe(f"tribe{self.tribe_id}")
                    if msg.get("push_message_type") == "tribe_kick":
                        self.unset_info(tribe=True)

                    if handler := (self.handlers.get(msg.get('push_message_type'))):
                        Thread(target=handler, args=[msg]).start()
            except Exception as e:
                if self.will_reconnect.is_set():  # Planned disconnection
                    self.will_reconnect.clear()
                elif self.connected:  # Unexpected disconnection
                    self.connected = False
                    logging.error(f"Error receiving data: {e}")
                break
