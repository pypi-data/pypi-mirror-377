
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import os
import pickle

# In-memory storage
encrypted_files = {}

# Hidden folder for encrypted files
hidden_folder = Path(".encrypted")
hidden_folder.mkdir(exist_ok=True)

def encrypt_file_in_memory(filepath, password, save_to_disk=False):
    path = Path(filepath)
    if not path.exists():
        print(f"[WARN] {filepath} not found, skipping.")
        return

    data = path.read_text(encoding="utf-8")
    data_bytes = data.encode("utf-8")

    salt = os.urandom(16)
    iv = os.urandom(16)

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data_bytes) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    encrypted_files[path.stem] = (salt, iv, encrypted)
    print(f"[ENCRYPTED IN MEMORY] {filepath}")

    if save_to_disk:
        with open(hidden_folder / f"{path.stem}.pkl", "wb") as f:
            pickle.dump((salt, iv, encrypted), f)
        print(f"[SAVED TO DISK] {hidden_folder / f'{path.stem}.pkl'}")

def load_encrypted_file(name):
    file_path = hidden_folder / f"{name}.pkl"
    if not file_path.exists():
        print(f"[ERROR] {file_path} not found.")
        return
    with open(file_path, "rb") as f:
        encrypted_files[name] = pickle.load(f)
    print(f"[LOADED INTO MEMORY] {name}")

def decrypt_and_print(name, password):
    if name not in encrypted_files:
        print(f"[ERROR] {name} not found in memory")
        return
    salt, iv, encrypted = encrypted_files[name]
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200_000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    code_text = decrypted.decode("utf-8")
    print(f"\n--- Code of {name} ---")
    print(code_text)
    return code_text

def run_file_in_memory(name, password):
    code_text = decrypt_and_print(name, password)
    exec(code_text, globals())
