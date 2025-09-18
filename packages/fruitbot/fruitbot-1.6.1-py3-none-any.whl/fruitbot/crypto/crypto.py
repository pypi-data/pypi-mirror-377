import base64
import urllib.parse
from typing import Optional
from itertools import cycle

class Encryption:
    def __init__(self, is_socket=False, version=None, key: Optional[bytes] = None):
        if key:
            self.key = key
        elif is_socket:
            self.key = b'floatint201412bool23string'
        elif version == 2:
            self.key = b'mwBSDp1nMhcdCravltVGADXTFx7bN9mr0XMgyDezIJghf65lvXhRdLWrScCk'
        else:
            self.key = b'ali1343faraz1055antler288based'
        self.requires_double_encryption = is_socket
        self.version = version or 1

    def encrypt(self, message: str) -> str:
        """Encrypts a message using XOR encryption."""
        message_bytes = message.encode('utf-8')
        if self.requires_double_encryption:
            message_bytes = base64.b64encode(message_bytes)
        output_bytes = bytes(m ^ k for m, k in zip(message_bytes, cycle(self.key)))
        encoded = base64.b64encode(output_bytes).decode('utf-8')
        return encoded if self.requires_double_encryption else urllib.parse.quote(encoded)

    def decrypt(self, encrypted: str) -> str:
        """Decrypts an encrypted message using XOR decryption."""
        try:
            unquoted = urllib.parse.unquote(encrypted)
            if encrypted.startswith("{"):
                return encrypted
            encrypted_bytes = base64.b64decode(unquoted)
        except (ValueError, base64.binascii.Error) as err:
            print(f"Error during decoding: {err}")
            return ""

        decrypted_bytes = bytes(e ^ k for e, k in zip(encrypted_bytes, cycle(self.key)))
        if self.requires_double_encryption:
            decrypted_bytes = base64.b64decode(decrypted_bytes)
        return decrypted_bytes.decode('utf-8', errors='ignore')
