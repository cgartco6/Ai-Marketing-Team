import pytest
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
import hashlib
import psutil
import socket
import subprocess

# Import security components to test
from core.crypto import MilitaryCrypto
from agents.sentinel import SecuritySentinel
from core.utils import hash_data, secure_fetch

# Test data
SAMPLE_ENCRYPTED_DATA = {
    'payload': 'gAAAAABlXrX8J0X9z3Z5Q6k7V1nYqW0pLx4eG3vB2mN6cRtFhYdD1oPw==',
    'encrypted': True
}

# ----- Cryptographic Tests -----
class TestMilitaryCrypto:
    def test_init(self):
        crypto = MilitaryCrypto()
        assert isinstance(crypto.key, bytes)
        assert len(crypto.key) == 44  # Fernet key length
        assert isinstance(crypto.cipher, Fernet)

    def test_encrypt_decrypt(self):
        crypto = MilitaryCrypto()
        test_data = "Top secret marketing data"
        
        encrypted = crypto.encrypt(test_data)
        decrypted = crypto.decrypt(encrypted)
        
        assert isinstance(encrypted, str)
        assert encrypted != test_data
        assert decrypted == test_data

    def test_secure_comms(self):
        crypto = MilitaryCrypto()
        message = {"action": "launch", "target": "campaign_123"}
        secure_payload = crypto.secure_comms("sender", "receiver", message)
        
        assert isinstance(secure_payload, dict)
        assert 'sender' in secure_payload
        assert 'receiver' in secure_payload
        assert 'message' in secure_payload

    def test_decrypt_failure(self):
        crypto = MilitaryCrypto()
        with pytest.raises(Exception):
            crypto.decrypt("invalid_encrypted_data")

# ----- Security Sentinel Tests -----
class TestSecuritySentinel:
    @pytest.fixture
    def sentinel(self, crypto):
        return SecuritySentinel(crypto)

    def test_initial_state(self, sentinel):
        assert sentinel.threat_level == 0
        assert sentinel.active_countermeasures == []
        assert isinstance(sentinel.whitelist, dict)
        assert isinstance(sentinel.threat_signatures, dict)

    @patch('psutil.net_connections')
    def test_network_monitoring(self, mock_net, sentinel):
        mock_net.return_value = [
            MagicMock(
                laddr=MagicMock(ip='127.0.0.1', port=8000),
                raddr=MagicMock(ip='192.168.1.100', port=9000),
                status='ESTABLISHED',
                pid=1234
            )
        ]
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._monitor_network_activity()
            assert mock_handle.called

    @patch('psutil.process_iter')
    def test_process_monitoring(self, mock_procs, sentinel):
        mock_procs.return_value = [
            MagicMock(pid=9999, info={'name': 'suspicious.exe', 'exe': 'C:/malware.exe'})
        ]
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._monitor_processes()
            assert mock_handle.called

    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_performance_monitoring(self, mock_mem, mock_cpu, sentinel):
        mock_cpu.return_value = 95  # High CPU usage
        mock_mem.return_value = MagicMock(percent=90)  # High memory usage
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._monitor_system_performance()
            assert mock_handle.call_count == 2  # CPU and memory alerts

    @patch('os.path.exists')
    @patch('builtins.open')
    def test_file_integrity_check(self, mock_open, mock_exists, sentinel):
        mock_exists.return_value = True
        mock_open.return_value.__enter__.return_value.read.return_value = b"test data"
        
        # Simulate file modification by returning different hash
        with patch.object(sentinel, '_hash_file', return_value="modified_hash"):
            sentinel.integrity_baseline = {'test_file.txt': 'original_hash'}
            with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
                sentinel._check_system_integrity()
                assert mock_handle.called

    def test_threat_level_management(self, sentinel):
        sentinel._update_threat_level(5)
        assert sentinel.threat_level == 5
        
        sentinel._update_threat_level(-3)
        assert sentinel.threat_level == 2  # Doesn't go below 0
        
        sentinel._update_threat_level(15)
        assert sentinel.threat_level == 10  # Doesn't exceed 10

    @patch('subprocess.run')
    def test_lockdown_protocol(self, mock_run, sentinel):
        sentinel._activate_lockdown()
        
        assert 'lockdown' in sentinel.active_countermeasures
        assert mock_run.called  # Network isolation commands

    def test_whitelist_verification(self, sentinel):
        # Test authorized process
        authorized_proc = {'name': 'python.exe', 'exe': 'C:/Python/python.exe'}
        assert sentinel._is_process_whitelisted(authorized_proc)
        
        # Test unauthorized process
        unauthorized_proc = {'name': 'malware.exe', 'exe': 'C:/temp/malware.exe'}
        assert not sentinel._is_process_whitelisted(unauthorized_proc)

# ----- Core Security Utility Tests -----
class TestSecurityUtils:
    def test_hash_data(self):
        test_string = "secure_data_123"
        hashed = hash_data(test_string)
        
        assert isinstance(hashed, str)
        assert len(hashed) == 64  # SHA256 length
        assert hashed == hashlib.sha256(test_string.encode()).hexdigest()

    @patch('configparser.ConfigParser.read')
    @patch('configparser.ConfigParser.has_option')
    def test_secure_fetch(self, mock_has_opt, mock_read):
        mock_has_opt.return_value = True
        mock_read.return_value = None
        
        # Mock configparser to return test key
        with patch('configparser.ConfigParser.__getitem__', 
                  return_value={'API_KEY': 'test_key_123'}):
            key = secure_fetch('API_KEY')
            assert key == 'test_key_123'

    def test_secure_fetch_failure(self):
        with pytest.raises(ValueError):
            secure_fetch('NON_EXISTENT_KEY')

# ----- Integration Security Tests -----
class TestSecurityIntegration:
    @patch('agents.sentinel.SecuritySentinel._send_results')
    def test_commander_to_sentinel_alert_flow(self, mock_send):
        crypto = MilitaryCrypto()
        commander = ProjectCommander(crypto)
        sentinel = SecuritySentinel(crypto)
        
        # Simulate message passing
        commander.send_message = sentinel.receive_message
        commander.send_message(sentinel.name, {
            'type': 'threat_alert',
            'threat': {
                'description': 'Unauthorized access attempt',
                'severity': 8,
                'source': 'network_monitor'
            }
        })
        
        time.sleep(0.2)  # Allow processing
        assert mock_send.called
        assert sentinel.threat_level == 8

    def test_encrypted_comms_flow(self):
        crypto = MilitaryCrypto()
        test_message = {"action": "analyze", "target": "campaign_456"}
        
        # Encrypt from commander's perspective
        encrypted = crypto.secure_comms("Commander", "Profiler", test_message)
        
        # Decrypt from profiler's perspective
        decrypted = json.loads(crypto.decrypt(encrypted['message']))
        
        assert decrypted == test_message

# ----- Real-World Attack Simulation Tests -----
class TestAttackScenarios:
    @patch('psutil.process_iter')
    def test_crypto_miner_detection(self, mock_procs, crypto):
        sentinel = SecuritySentinel(crypto)
        mock_procs.return_value = [
            MagicMock(info={'name': 'legit_app.exe'}),
            MagicMock(info={'name': 'xmrig.exe'})  # Known crypto miner
        ]
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._monitor_processes()
            assert mock_handle.called
            assert "xmrig" in str(mock_handle.call_args)

    @patch('psutil.net_connections')
    def test_data_exfiltration_attempt(self, mock_net, crypto):
        sentinel = SecuritySentinel(crypto)
        mock_net.return_value = [
            MagicMock(
                laddr=MagicMock(ip='192.168.1.50', port=1234),
                raddr=MagicMock(ip='45.33.12.75', port=5555),  # Known bad IP
                status='ESTABLISHED'
            )
        ]
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._monitor_network_activity()
            assert mock_handle.called
            assert "45.33.12.75" in str(mock_handle.call_args)

    def test_config_tampering_detection(self, crypto, tmp_path):
        sentinel = SecuritySentinel(crypto)
        test_file = tmp_path / "critical_config.ini"
        test_file.write_text("original_content")
        
        # Establish baseline
        sentinel.integrity_baseline = {str(test_file): hash_data("original_content")}
        
        # Tamper with file
        test_file.write_text("modified_by_hacker")
        
        with patch.object(sentinel, '_handle_suspicious_activity') as mock_handle:
            sentinel._check_system_integrity()
            assert mock_handle.called
            assert "modified" in str(mock_handle.call_args)

if __name__ == "__main__":
    pytest.main(["-v", "tests/test_security.py"])
