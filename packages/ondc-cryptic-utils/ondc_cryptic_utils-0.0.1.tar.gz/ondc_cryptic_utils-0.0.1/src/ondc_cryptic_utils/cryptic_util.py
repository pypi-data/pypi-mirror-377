"""
A utility class for cryptographic operations used in the ONDC protocol.

This class handles key generation, message signing, signature verification,
and message encryption/decryption using Ed25519 for signing and X25519
with AES-ECB for encryption. It is based on the ONDC reference implementation
for cryptographic utilities.
"""
import json
import re
import time
from typing import Optional

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from nacl.bindings import crypto_sign_ed25519_sk_to_seed
from nacl.encoding import Base64Encoder
from nacl.hash import blake2b
from nacl.signing import SigningKey, VerifyKey


class settings:
    ONDC_SIGNING_PUBLIC_KEY = ""
    ONDC_SIGNING_PRIVATE_KEY = ""
    ONDC_ENCRYPTION_PUBLIC_KEY = ""
    ONDC_ENCRYPTION_PRIVATE_KEY = ""


class OndcCrypticUtil:
    """
    Handles cryptographic operations for ONDC, including signing, verification, and encryption/decryption.

    The methods are based on the ONDC reference implementation and use specific
    cryptographic libraries for compliance.

    refer this documentation:
    https://github.com/ONDC-Official/reference-implementations/blob/main/utilities/signing_and_verification/python/cryptic_utils.py
    """

    def __init__(
        self,
        signing_public_key=settings.ONDC_SIGNING_PUBLIC_KEY,
        signing_private_key=settings.ONDC_SIGNING_PRIVATE_KEY,
        encryption_public_key=settings.ONDC_ENCRYPTION_PUBLIC_KEY,
        encryption_private_key=settings.ONDC_ENCRYPTION_PRIVATE_KEY,
    ):
        self.signing_public_key = signing_public_key
        self.signing_private_key = signing_private_key
        self.encryption_public_key = encryption_public_key
        self.encryption_private_key = encryption_private_key

    @staticmethod
    def generate_key_pairs():
        """
        Generates a pair of Ed25519 signing key and X25519 encryption key pairs.

        Returns a dictionary of two key pairs: "signing" and "encryption".
        Each key pair contains a "private_key" and "public_key" encoded in Base64.
        """
        signing_key = SigningKey.generate()
        private_key = Base64Encoder.encode(signing_key._signing_key).decode()
        public_key = Base64Encoder.encode(bytes(signing_key.verify_key)).decode()
        inst_private_key = X25519PrivateKey.generate()
        inst_public_key = inst_private_key.public_key()
        bytes_private_key = inst_private_key.private_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        bytes_public_key = inst_public_key.public_bytes(
            encoding=serialization.Encoding.DER,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        encryption_private_key = Base64Encoder.encode(bytes_private_key).decode("utf-8")
        encryption_public_key = Base64Encoder.encode(bytes_public_key).decode("utf-8")
        return {
            "Signing_private_key": private_key,
            "Signing_public_key": public_key,
            "Encryption_Privatekey": encryption_private_key,
            "Encryption_Publickey": encryption_public_key,
        }

    def create_signing_string(
        self, message: str, created: Optional[int] = None, expires: int = 3600
    ):
        if created is None:
            created = int(time.time())

        expires = created + expires

        digest = blake2b(message.encode(), digest_size=64, encoder=Base64Encoder)
        digest_base64 = digest.decode()
        return f"(created): {created}\n(expires): {expires}\ndigest: BLAKE-512={digest_base64}"

    def sign_message(self, signing_string):
        private_key64 = Base64Encoder.decode(self.signing_private_key)
        seed = crypto_sign_ed25519_sk_to_seed(private_key64)
        signed_message = SigningKey(seed).sign(signing_string.encode())
        return Base64Encoder.encode(signed_message.signature).decode()

    def verify_signature(self, signature, signing_key):
        try:
            public_key64 = Base64Encoder.decode(self.signing_public_key)
            VerifyKey(public_key64).verify(
                bytes(signing_key, "utf8"), Base64Encoder.decode(signature)
            )
            return True
        except Exception:
            return False

    def encrypt_message(self, message):
        private_key = serialization.load_der_private_key(
            Base64Encoder.decode(self.encryption_private_key), password=None
        )
        public_key = serialization.load_der_public_key(
            Base64Encoder.decode(self.encryption_public_key)
        )
        shared_key = private_key.exchange(public_key)
        cipher = AES.new(shared_key, AES.MODE_ECB)
        return Base64Encoder.encode(
            cipher.encrypt(pad(message.encode("utf-8"), AES.block_size))
        ).decode("utf-8")

    def decrypt_message(
        self, cipherstring, encryption_private_key=None, encryption_public_key=None
    ):
        if encryption_private_key is not None:
            self.encryption_private_key = encryption_private_key
        if encryption_public_key is not None:
            self.encryption_public_key = encryption_public_key
        private_key = serialization.load_der_private_key(
            Base64Encoder.decode(encryption_private_key), password=None
        )
        public_key = serialization.load_der_public_key(
            Base64Encoder.decode(encryption_public_key)
        )
        shared_key = private_key.exchange(public_key)
        cipher = AES.new(shared_key, AES.MODE_ECB)
        ciphertxt = Base64Encoder.decode(cipherstring)
        # print(AES.block_size, len(ciphertxt))
        return unpad(cipher.decrypt(ciphertxt), AES.block_size).decode("utf-8")


"""
A utility class for creating and verifying ONDC authorization headers.

This class leverages OndcCrypticUtil to handle the complex process of
signing a request body and formatting the signature into an
"Authorization" header, as well as verifying an incoming header.
"""
class OndcAuthUtil():
    """
    Handles the creation and verification of ONDC-compliant authorization headers.

    This class encapsulates the logic for preparing request payloads for signing,
    generating the authorization header, and validating received headers and their
    associated request bodies.
    """
    cryptic_util = OndcCrypticUtil()

    def create_authorization_header(self, subscriber_id, unique_key_id, message, expires=3600):
        created = int(time.time())
        expires = created + expires
        message = json.dumps(message)
        signing_string = self.cryptic_util.create_signing_string(message, created, expires)
        signature = self.cryptic_util.sign_message(signing_string)

        header = (
            f'Signature keyId="{subscriber_id}|{unique_key_id}|ed25519",'
            f'algorithm="ed25519",created="{created}",expires="{expires}",'
            f'headers="(created) (expires) digest",signature="{signature}"'
        )

        return header

    def verify_authorisation_header(self, auth_header, request_body):
        try:
            # Extract components from the authorization header
            components = {}
            pattern = re.compile(r'(\w+)="([^"]*)"|\w+=\w+')
            for match in pattern.finditer(auth_header.replace("Signature ", "")):
                if match.group(2):
                    components[match.group(1)] = match.group(2)
                else:
                    key, value = match.group(0).split("=")
                    components[key] = value

            signature = components["signature"]
            created = int(components["created"])
            expires = int(components["expires"])

            # Verify timestamp
            current_time = int(time.time())
            if current_time < created or current_time > expires:
                return False, "Timestamp verification failed"

            # Recreate the signing string
            request_body = json.dumps(request_body)
            signing_string = self.cryptic_util.create_signing_string(request_body, created, expires)
            if self.cryptic_util.verify_signature(signature, signing_string):
                return True, "Signature verified successfully"
            else:
                return False, "Signature verification failed"

        except Exception as e:
            return False, f"Error in verifying authorization header: {str(e)}"
