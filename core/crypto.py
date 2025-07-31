from cryptography.fernet import Fernet
import hashlib
import os

class MilitaryCrypto:
    def __init__(self, key=None):
        self.key = key or Fernet.generate_key()
        self.cipher = Fernet(self.key)
        
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def hash_data(self, data):
        return hashlib.sha256(data.encode()).hexdigest()[:12]
    
    def secure_comms(self, sender, receiver, message):
        return {
            'sender': sender,
            'receiver': receiver,
            'payload': self.encrypt(json.dumps(message))
        }
