# ONDC Cryptic Utils

A Python library providing cryptographic utilities for the Open Network for Digital Commerce (ONDC) protocol. This library implements the cryptographic operations required for secure communication within the ONDC ecosystem, including message signing, signature verification, encryption/decryption, and authorization header management.

## Features

### Core Cryptographic Operations

- **Ed25519 Digital Signatures**: Generate and verify digital signatures using Ed25519 algorithm
- **X25519 Key Exchange**: Implement key exchange for secure communication
- **AES Encryption**: Message encryption and decryption using AES in ECB mode
- **BLAKE2b Hashing**: Generate message digests using BLAKE2b-512

### ONDC Protocol Support

- **Key Pair Generation**: Generate Ed25519 signing keys and X25519 encryption keys
- **Authorization Headers**: Create and verify ONDC-compliant authorization headers
- **Message Signing**: Sign request payloads according to ONDC specifications
- **Signature Verification**: Validate incoming signed messages and headers
- **Timestamp Validation**: Verify message freshness using created/expires timestamps

## Installation

Install the package using pip:

```bash
pip install ondc-cryptic-utils
```

Or install in development mode:

```bash
pip install -e .
```

## Quick Start

### Basic Usage

```python
from ondc_cryptic_utils import OndcCrypticUtil, OndcAuthUtil

# Initialize the cryptographic utility
crypto_util = OndcCrypticUtil(
    signing_private_key="your_signing_private_key",
    signing_public_key="your_signing_public_key",
    encryption_private_key="your_encryption_private_key",
    encryption_public_key="your_encryption_public_key"
)

# Generate new key pairs
key_pairs = OndcCrypticUtil.generate_key_pairs()
print("Generated keys:", key_pairs)
```

### Creating Authorization Headers

```python
from ondc_cryptic_utils import OndcAuthUtil
import json

# Initialize auth utility
auth_util = OndcAuthUtil()

# Create authorization header for a request
message = {"context": {"action": "search"}, "message": {}}
subscriber_id = "your_subscriber_id"
unique_key_id = "your_unique_key_id"

auth_header = auth_util.create_authorization_header(
    subscriber_id=subscriber_id,
    unique_key_id=unique_key_id,
    message=message,
    expires=3600  # Optional: expires in seconds
)

print("Authorization header:", auth_header)
```

### Verifying Authorization Headers

```python
# Verify an incoming authorization header
auth_header = 'Signature keyId="subscriber|key|ed25519",...'
request_body = {"context": {"action": "search"}}

is_valid, message = auth_util.verify_authorisation_header(auth_header, request_body)
if is_valid:
    print("Authorization verified successfully")
else:
    print(f"Authorization failed: {message}")
```

### Message Encryption and Decryption

```python
# Encrypt a message
message = "Hello, ONDC!"
encrypted = crypto_util.encrypt_message(message)
print("Encrypted:", encrypted)

# Decrypt the message
decrypted = crypto_util.decrypt_message(
    encrypted,
    encryption_private_key="recipient_private_key",
    encryption_public_key="sender_public_key"
)
print("Decrypted:", decrypted)
```

## Configuration

The library uses a `settings` class for default key configuration:

```python
class settings:
    ONDC_SIGNING_PUBLIC_KEY = "your_default_signing_public_key"
    ONDC_SIGNING_PRIVATE_KEY = "your_default_signing_private_key"
    ONDC_ENCRYPTION_PUBLIC_KEY = "your_default_encryption_public_key"
    ONDC_ENCRYPTION_PRIVATE_KEY = "your_default_encryption_private_key"
```

You can override these by passing keys directly to the `OndcCrypticUtil` constructor.

## Dependencies

- **pycryptodomex**: AES encryption/decryption operations
- **cryptography**: X25519 key exchange and serialization
- **PyNaCl**: Ed25519 signing, BLAKE2b hashing, and Base64 encoding

## Compliance

This library is based on the official ONDC reference implementation for cryptographic utilities and follows the ONDC protocol specifications for:

- Digital signature format and verification
- Authorization header structure
- Message encryption standards
- Key generation and management

## Testing

To run the tests, install the package in development mode and run:

```bash
python3 -m unittest discover tests
```

## Contributing

Contributions are welcome! Please ensure all changes maintain compatibility with the ONDC protocol specifications.

## License

This project is licensed under the MIT License.

## References

- [ONDC Official Reference Implementation](https://github.com/ONDC-Official/reference-implementations/blob/main/utilities/signing_and_verification/python/cryptic_utils.py)
- [ONDC Protocol Documentation](https://ondc.org/)
