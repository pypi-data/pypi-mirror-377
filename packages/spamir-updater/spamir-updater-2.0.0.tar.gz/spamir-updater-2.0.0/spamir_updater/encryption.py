import hashlib
import hmac
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding


class EncryptionHandler:
    def __init__(self, auth_token, encryption_iterations=100000):
        self.auth_token = auth_token
        self.encryption_iterations = encryption_iterations
        self.current_channel_key = None
    
    def negotiate_secure_layer(self, client_nonce_b64, server_nonce_b64):
        if not client_nonce_b64 or not server_nonce_b64:
            return False
        
        try:
            client_nonce_padded = client_nonce_b64 + '=='
            server_nonce_padded = server_nonce_b64 + '=='
            client_marker_bytes = base64.urlsafe_b64decode(client_nonce_padded)
            server_marker_bytes = base64.urlsafe_b64decode(server_nonce_padded)
            kdf_salt_material = client_marker_bytes + server_marker_bytes
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=kdf_salt_material,
                iterations=self.encryption_iterations,
                backend=default_backend()
            )
            
            self.current_channel_key = kdf.derive(self.auth_token.encode('utf-8'))
            
            return True
        except Exception as e:
            print(f"Error negotiating secure layer: {e}")
            self.current_channel_key = None
            return False
    
    def encrypt_payload(self, raw_data_bytes):
        if not self.current_channel_key:
            return None
        
        try:
            iv = os.urandom(16)
            cipher = Cipher(
                algorithms.AES(self.current_channel_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(raw_data_bytes) + padder.finalize()
            encrypted = encryptor.update(padded_data) + encryptor.finalize()
            combined = iv + encrypted
            return base64.b64encode(combined).decode('ascii')
        except Exception as e:
            print(f"Encryption error: {e}")
            return None
    
    def decrypt_payload(self, encrypted_data_b64):
        if not self.current_channel_key:
            return None
        
        try:
            combined = base64.b64decode(encrypted_data_b64)
            iv = combined[:16]
            ciphertext = combined[16:]
            cipher = Cipher(
                algorithms.AES(self.current_channel_key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            
            return plaintext
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def sign_data(self, data):
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            raise TypeError('Data for HMAC signing must be string or bytes')
        
        signature = hmac.new(
            self.auth_token.encode('utf-8'),
            data_bytes,
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, data, signature):
        computed_signature = self.sign_data(data)
        return hmac.compare_digest(computed_signature, signature)
    
    def generate_nonce(self):
        nonce = os.urandom(16)
        return base64.urlsafe_b64encode(nonce).decode('ascii').rstrip('=')
    
    def compute_hash(self, data):
        return hashlib.sha256(data).hexdigest()