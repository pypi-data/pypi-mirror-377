import unittest

from src.ondc_cryptic_utils.cryptic_util import OndcCrypticUtil


class TestOndcCrypticUtil(unittest.TestCase):

    def test_generate_key_pairs(self):
        key_pairs = OndcCrypticUtil.generate_key_pairs()
        self.assertIn('Signing_private_key', key_pairs)
        self.assertIn('Signing_public_key', key_pairs)
        self.assertIn('Encryption_Privatekey', key_pairs)
        self.assertIn('Encryption_Publickey', key_pairs)

    def test_sign_and_verify(self):
        key_pairs = OndcCrypticUtil.generate_key_pairs()
        cryptic_util = OndcCrypticUtil(
            signing_private_key=key_pairs['Signing_private_key'],
            signing_public_key=key_pairs['Signing_public_key']
        )
        message = "test message"
        signing_string = cryptic_util.create_signing_string(message)
        signature = cryptic_util.sign_message(signing_string)
        self.assertTrue(cryptic_util.verify_signature(signature, signing_string))

    def test_encrypt_and_decrypt(self):
        key_pairs = OndcCrypticUtil.generate_key_pairs()
        cryptic_util = OndcCrypticUtil(
            encryption_private_key=key_pairs['Encryption_Privatekey'],
            encryption_public_key=key_pairs['Encryption_Publickey']
        )
        message = "test message"
        encrypted_message = cryptic_util.encrypt_message(message)
        decrypted_message = cryptic_util.decrypt_message(
            encrypted_message,
            encryption_private_key=key_pairs['Encryption_Privatekey'],
            encryption_public_key=key_pairs['Encryption_Publickey']
        )
        self.assertEqual(message, decrypted_message)

if __name__ == '__main__':
    unittest.main()
