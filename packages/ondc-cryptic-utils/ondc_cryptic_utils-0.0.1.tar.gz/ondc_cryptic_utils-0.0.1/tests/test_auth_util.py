import unittest

from src.ondc_cryptic_utils.cryptic_util import OndcAuthUtil, OndcCrypticUtil


class TestOndcAuthUtil(unittest.TestCase):

    def test_create_and_verify_authorization_header(self):
        key_pairs = OndcCrypticUtil.generate_key_pairs()
        auth_util = OndcAuthUtil()
        auth_util.cryptic_util.signing_private_key = key_pairs['Signing_private_key']
        auth_util.cryptic_util.signing_public_key = key_pairs['Signing_public_key']

        subscriber_id = "test_subscriber"
        unique_key_id = "test_key_id"
        message = {"test": "message"}

        header = auth_util.create_authorization_header(subscriber_id, unique_key_id, message)
        is_valid, error = auth_util.verify_authorisation_header(header, message)

        self.assertTrue(is_valid)
        self.assertEqual(error, "Signature verified successfully")

    def test_verify_authorization_header_fail(self):
        key_pairs1 = OndcCrypticUtil.generate_key_pairs()
        key_pairs2 = OndcCrypticUtil.generate_key_pairs()
        auth_util1 = OndcAuthUtil()
        auth_util1.cryptic_util.signing_private_key = key_pairs1['Signing_private_key']
        auth_util1.cryptic_util.signing_public_key = key_pairs1['Signing_public_key']

        auth_util2 = OndcAuthUtil()
        auth_util2.cryptic_util.signing_public_key = key_pairs2['Signing_public_key']

        subscriber_id = "test_subscriber"
        unique_key_id = "test_key_id"
        message = {"test": "message"}

        header = auth_util1.create_authorization_header(subscriber_id, unique_key_id, message)
        is_valid, error = auth_util2.verify_authorisation_header(header, message)

        self.assertFalse(is_valid)
        self.assertEqual(error, "Signature verification failed")

if __name__ == '__main__':
    unittest.main()
