# pip install pycryptodome cryptography

import os
from Crypto.PublicKey import RSA


class CryptoKeyOps:
    """
    This is a crypto library to:
     manage key files
     encrypt keys
     decrypt keys

    Typical use is to:
     step 0: assumes we have a locally stored private key that is encrypted at 'encrypted_key_filepath'
     step 1: get the PASSPHRASE dynamically from a command argument
     step 2: create an object to 'crypto_ops = CryptoKeyOps()'
     step 3: use the PASSPHRASE to decrypt key with 'get_decrypted_key_path_from_encrypted_key_path(encrypted_key_filepath, PASSPHRASE)'
     step 4: perform needed actions with
     step 5: destroy the temporary unencrypted key (IMPORTANT)

    """

    def __init__(self) -> None:
        pass

    def _read_key_file(self, unencrypted_key_filepath):
        key_bytes = open(unencrypted_key_filepath, "rb").read()
        return key_bytes

    def _get_key_obj(self, key_str):
        key_obj = RSA.import_key(key_str)
        return key_obj

    def _encrypt_key_obj(self, unencrypted_key_obj, passphrase):
        encrypted_key_obj = unencrypted_key_obj.export_key(passphrase=passphrase)
        return encrypted_key_obj

    def _decrypt_key_str(self, encrypted_key_str, passphrase):
        decrypted_key_obj = RSA.import_key(encrypted_key_str, passphrase=passphrase)
        return decrypted_key_obj

    def _export_key_obj(self, key_obj):
        out_key_str = key_obj.exportKey(format="PEM", passphrase=None, pkcs=1, protection=None).decode("utf-8")
        return out_key_str

    def verify_keys_match(self, key1, key2):
        if key1 == key2:
            print(f"keys match")
            return True
        else:
            print(f"keys DO NOT match")
            return False

    def save_key_bytes_to_file(self, key_bytes, filepath):
        with open(filepath, "wb") as f:
            f.write(key_bytes)
            f.close()
        return key_bytes

    def save_key_str_to_file(self, key_str, filepath):
        with open(filepath, "w") as f:
            f.write(key_str)
            f.close()
        return key_str

    def key_object_to_str(self, key_obj):
        return self._export_key_obj(key_obj)

    def encrypt_key_from_str(self, unencrypted_key_str, passphrase):
        self.unencrypted_key_obj = self._get_key_obj(unencrypted_key_str)
        self.encrypted_key_bytes = self._encrypt_key_obj(self.unencrypted_key_obj, passphrase)
        return self.encrypted_key_bytes

    def encrypt_key_from_file(self, filepath, passphrase):
        self.unencrypted_key_str = self._read_key_file(filepath)
        self.encrypted_key_bytes = self.encrypt_key_from_str(self.unencrypted_key_str, passphrase)
        return self.encrypted_key_bytes

    def decrypt_key(self, encrypted_key_obj, passphrase):
        self.decrypted_key_obj = self._decrypt_key_str(encrypted_key_obj, passphrase)
        self.decrypted_key_bytes = self.decrypted_key_obj.export_key()
        return self.decrypted_key_bytes

    def decrypt_key_from_file(self, filepath, passphrase):
        self.key_str = self._read_key_file(filepath)
        self.decrypted_key_str = self.decrypt_key(self.key_str, passphrase)
        return self.decrypted_key_str

    def get_decrypted_key_path_from_encrypted_key_path(
        self, encrypted_key_filepath: str, passphrase, decrypted_key_filepath: str = None
    ) -> str:
        """
        This aggregate function takes a filepath to an encrypted key, decrypts it, and saves to decrypted file
        By default this will save the decrypted file as same name + '.decrypted' to same folder
         unless you specify 'decrypted_key_filepath'

        Args:
            encrypted_key_filepath (str): full filepath to encrypted key
            decrypted_key_filepath (str, optional): full filepath to save decrypted file

        Returns:
            str: decrypted_key_filepath
        """
        encrypted_key_directory_path = os.path.split(encrypted_key_filepath)[0]
        encrypted_key_filename = os.path.split(encrypted_key_filepath)[1]
        if decrypted_key_filepath is None:
            decrypted_key_filename = f"{encrypted_key_filename}.decrypted"
            decrypted_key_filepath = os.path.join(encrypted_key_directory_path, decrypted_key_filename)

        decrypted_key_bytes = self.decrypt_key_from_file(encrypted_key_filepath, passphrase)
        self.save_key_bytes_to_file(decrypted_key_bytes, decrypted_key_filepath)

        return decrypted_key_filepath


if __name__ == "__main__":
    """
    These are some tests to verify correct operation of the crypto functions
    Typical use is to:
     step 0: assumes we have a locally stored private key that is encrypted at 'encrypted_key_filepath'
     step 1: get the PASSPHRASE dynamically from a command argument
     step 2: create an object to 'crypto_ops = CryptoKeyOps()'
     step 3: use the PASSPHRASE to decrypt key with 'get_decrypted_key_path_from_encrypted_key_path(encrypted_key_filepath, PASSPHRASE)'
     step 4: perform needed actions with
     step 5: destroy the temporary unencrypted key (IMPORTANT)

    """
    PASSPHRASE = "password"
    unencrypted_key_filepath = "dev/api_secret.txt"
    encrypted_key_filepath = "dev/encrypted.txt"
    decrypted_key_filepath = "dev/decrypted.txt"
    crypto_ops = CryptoKeyOps()

    original_key_bytes = crypto_ops._read_key_file(unencrypted_key_filepath)
    encrypted_key_bytes = crypto_ops.encrypt_key_from_file(unencrypted_key_filepath, PASSPHRASE)
    crypto_ops.save_key_bytes_to_file(encrypted_key_bytes, encrypted_key_filepath)
    decrypted_key_bytes = crypto_ops.decrypt_key_from_file(encrypted_key_filepath, PASSPHRASE)
    crypto_ops.save_key_bytes_to_file(decrypted_key_bytes, decrypted_key_filepath)
    crypto_ops.verify_keys_match(original_key_bytes, decrypted_key_bytes)
    decrypted_key_filepath = crypto_ops.get_decrypted_key_path_from_encrypted_key_path(
        encrypted_key_filepath, PASSPHRASE
    )
    print(f"decrypted_key_filepath: {decrypted_key_filepath}")
    os.remove(decrypted_key_filepath)
