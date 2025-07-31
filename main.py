import os
import threading
import configparser
from agents.commander import ProjectCommander
from core.crypto import MilitaryCrypto
from core.security import SecurityMonitor

def load_config():
    config = configparser.ConfigParser()
    config.read('config/settings.ini')
    config.read('config/api_keys.ini')
    return config

def main():
    # Initialize system
    config = load_config()
    crypto = MilitaryCrypto(key=config['SECURITY']['ENCRYPTION_KEY'].encode())
    
    # Create agents
    commander = ProjectCommander(crypto)
    
    # Start security monitoring
    security = SecurityMonitor()
    security_thread = threading.Thread(target=security.continuous_monitoring, daemon=True)
    security_thread.start()
    
    # Main interface
    while True:
        print("\nAI Marketing Command Center")
        print("1. Launch New Campaign")
        print("2. Exit")
        choice = input("Select: ")
        
        if choice == '1':
            # Campaign setup logic
            pass
        elif choice == '2':
            break

if __name__ == "__main__":
    main()
