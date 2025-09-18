import os
import base64
from typing import Union
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from ruamel.yaml import YAML, scalarstring
from ruamel.yaml.compat import StringIO


def derive_key_and_iv(
    password: str, salt: bytes, key_length: int, iv_length: int
) -> (bytes, bytes):
    backend = default_backend()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=key_length + iv_length,
        salt=salt,
        iterations=10000,  # OpenSSL's default PBKDF2 iterations
        backend=backend,
    )
    key_iv = kdf.derive(password.encode())
    return key_iv[:key_length], key_iv[key_length : key_length + iv_length]


def encrypt_value(plaintext: str, password: str) -> str:
    # Generate a random salt
    salt = os.urandom(8)
    key, iv = derive_key_and_iv(password, salt, 16, 16)

    # Pad the plaintext to be a multiple of the block size
    padder = padding.PKCS7(AES.block_size).padder()
    padded_plaintext = padder.update(plaintext.encode("utf-8")) + padder.finalize()

    # Encrypt the plaintext
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()

    # Prepend 'Salted__' and the salt
    encrypted_data = b"Salted__" + salt + ciphertext

    # Base64 encode the result
    return base64.b64encode(encrypted_data).decode("utf-8")


def decrypt_value(encrypted_data: str, password: str) -> str:
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    if encrypted_data_bytes[:8] != b"Salted__":
        raise ValueError("Invalid encrypted data: missing 'Salted__' prefix")

    salt = encrypted_data_bytes[8:16]
    ciphertext = encrypted_data_bytes[16:]

    key, iv = derive_key_and_iv(password, salt, 16, 16)

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

    # PKCS7 padding removal
    padding_length = padded_plaintext[-1]
    if isinstance(padding_length, int) and 1 <= padding_length <= 16:
        plaintext = padded_plaintext[:-padding_length]
    else:
        plaintext = padded_plaintext

    decrypted_value = plaintext.decode("utf-8").strip()

    # Strip outer quotes if they exist but are not intended to be part of the value
    if decrypted_value.startswith('"') and decrypted_value.endswith('"'):
        decrypted_value = decrypted_value[1:-1]

    return decrypted_value


def decrypt_yaml_values(data: Union[dict, list], password: str) -> Union[dict, list]:
    if isinstance(data, dict):
        decrypted = {
            key: decrypt_yaml_values(value, password) for key, value in data.items()
        }
        return decrypted
    elif isinstance(data, list):
        return [decrypt_yaml_values(item, password) for item in data]
    elif isinstance(data, str):
        try:
            decrypted_value = decrypt_value(data, password).strip()
            if '\n' in decrypted_value:
                return scalarstring.LiteralScalarString(decrypted_value)
            else:
                return decrypted_value
        except Exception:
            return data
    else:
        return data


def decrypt_yaml_file(file_path: str, password: str):
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True  # Preserve quotes around strings
    # yaml.explicit_start = True  # Ensure explicit start of the document

    with open(file_path, "r") as file:
        yaml_data = yaml.load(file)

    decrypted_data = decrypt_yaml_values(yaml_data, password)
    with open(f"{file_path}_decrypted", "w") as file:
        # with open(f"{file_path}", 'w') as file:
        yaml.dump(decrypted_data, file)


def encrypt_yaml_values(data: Union[dict, list], password: str) -> Union[dict, list]:
    if isinstance(data, dict):
        return {
            key: encrypt_yaml_values(value, password) for key, value in data.items()
        }
    elif isinstance(data, list):
        return [encrypt_yaml_values(item, password) for item in data]
    elif isinstance(data, str):
        return encrypt_value(data, password)
    else:
        return data


def encrypt_yaml_file(file_path: str, password: str):
    yaml = YAML()
    yaml.indent(sequence=4, offset=2)
    yaml.preserve_quotes = True  # Preserve quotes around strings
    # yaml.explicit_start = True  # Ensure explicit start of the document

    with open(f"{file_path}_decrypted", "r") as file:
        yaml_data = yaml.load(file)

    encrypted_data = encrypt_yaml_values(yaml_data, password)

    with StringIO() as output:
        yaml.dump(encrypted_data, output)
        yaml_str = output.getvalue().strip()  # Remove trailing newline

    with open(file_path, "w") as file:
        file.write(yaml_str)
