
# Codec according to double ratchet principle.

class DoubleRatchetCodec():
    def __init__(self, MAX_SKIP=20):
        # MAX_SKIP specifies the maximum number of message keys that can be skipped in a single chain.
        #
        # It should be set high enough to tolerate routine lost or delayed messages,
        # but low enough that a malicious sender can't trigger excessive recipient computation.
        self.MAX_SKIP = MAX_SKIP

        pass

    def GENERATE_DH(self):
        # Returns a new Diffie-Hellmann key pair.

        pass

    def DH(self, dh_pair, dh_pub):
        # Returns the output from the Diffie-Hellman calculation between the private key from the DH key pair dh_pair
        # and the DH public key dh_pub.
        #
        # If the DH function rejects invalid public keys, then this function
        # may raise an exception which terminates processing.

        pass

    def KDF_RK(self, rk, dh_out):
        # Returns a pair (32-byte root key, 32-byte chain key) as the output
        # of applying a KDF keyed by a 32-byte root key rk to some constant.

        pass

    def KDF_CK(self, ck):
        # Returns a pair (32-byte root key, 32-byte chain key) as the output
        # of applying a KDF keyed by a 32-byte chain key ck to some constant.

        pass

    def ENCRYPT(self, mk, plaintext, associated_data):
        # Returns an AEAD encryption of plaintext with message key mk.
        # The associated_data is authenticated but is not included in the ciphertext.
        # Because each message key is only used once, the AEAD nonce may handled in several ways:
        # - fixed to a constant;
        # - derived as an additional output from KDF_CK();
        # - or chosen randomly and transmitted.

        pass

    def DECRYPT(self, mk, ciphertext, associated_data):
        # Returns the AEAD decryption of ciphertext with message key mk.
        #
        # If authentication fails, an exception will be raised that terminates processing.

        pass

    def HEADER(self, dh_pair, pn, n):
        # Creates a new message header containing the DH ratchet public key from
        # - the key pair in dh_pair,
        # - the previous chain length pn,
        # - and the message number n.
        #
        # The returned header object contains ratched public key dh and integers pn and n.

        pass

    def CONCAT(self, ad, header):
        # Encodes a message header into a parseable byte sequence,
        # prepends the 'ad' byte sequence, and returns the result.
        #
        # If ad is not quaranteed to be a parseable byte sequence,
        # a length value should be prepended to the output
        # to ensure that the output is parseable as a unique pair (ad, header)

        pass

