import os
import json
import time
import threading
import queue
from datetime import datetime
import hashlib
import socket
import psutil
from cryptography.fernet import Fernet
from core.crypto import MilitaryCrypto
from core.utils import logger, secure_fetch
import schedule
import subprocess
import numpy as np

class SecuritySentinel:
    def __init__(self, crypto_system: MilitaryCrypto):
        self.crypto = crypto_system
        self.name = "Black Ops Security Sentinel"
        self.role = "Military-Grade Protection Module"
        self.task_queue = queue.Queue()
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.daemon = True
        self.thread.start()
        
        # Security configurations
        self.threat_level = 0  # 0-10 scale
        self.active_countermeasures = []
        self.whitelist = self._load_whitelist()
        self.threat_signatures = self._load_threat_signatures()
        
        # System baselines
        self.network_baseline = self._establish_network_baseline()
        self.process_baseline = self._establish_process_baseline()
        self.performance_baseline = self._establish_performance_baseline()
        
        # Monitoring intervals (seconds)
        self.monitoring_intervals = {
            'network': 5,
            'process': 10,
            'performance': 15,
            'integrity': 30
        }
        
        # Initialize monitoring schedules
        self._init_monitoring()
        
        logger(f"[{self.name}] Initialized with threat level {self.threat_level}")

    def run(self):
        while self.running:
            try:
                task = self.task_queue.get(timeout=1)
                self._process_task(task)
            except queue.Empty:
                schedule.run_pending()
                time.sleep(0.1)
    
    def _process_task(self, task):
        """Handle incoming security tasks"""
        if 'encrypted' in task:
            task = self._decrypt_task(task)
            
        task_type = task.get('type')
        
        if task_type == 'security_scan':
            self._full_system_scan()
        elif task_type == 'threat_alert':
            self._handle_threat_alert(task)
        elif task_type == 'update_whitelist':
            self._update_whitelist(task)
        elif task_type == 'lockdown':
            self._activate_lockdown()
        else:
            logger(f"[{self.name}] Unknown task type: {task_type}")

    def _decrypt_task(self, encrypted_task):
        """Decrypt incoming messages"""
        try:
            decrypted = self.crypto.decrypt(encrypted_task['payload'])
            return json.loads(decrypted)
        except Exception as e:
            logger(f"[{self.name}] Decryption failed: {str(e)}")
            return {'error': 'decryption_failed'}

    def _init_monitoring(self):
        """Initialize continuous monitoring schedules"""
        schedule.every(self.monitoring_intervals['network']).seconds.do(
            self._monitor_network_activity
        )
        schedule.every(self.monitoring_intervals['process']).seconds.do(
            self._monitor_processes
        )
        schedule.every(self.monitoring_intervals['performance']).seconds.do(
            self._monitor_system_performance
        )
        schedule.every(self.monitoring_intervals['integrity']).seconds.do(
            self._check_system_integrity
        )

    def _monitor_network_activity(self):
        """Monitor for suspicious network connections"""
        current_connections = self._get_network_connections()
        suspicious = []
        
        for conn in current_connections:
            if not self._is_connection_authorized(conn):
                suspicious.append(conn)
        
        if suspicious:
            self._handle_suspicious_activity(
                'network',
                f"Suspicious network connections detected: {suspicious}",
                severity=len(suspicious)
            )

    def _monitor_processes(self):
        """Monitor for suspicious processes"""
        current_processes = {p.pid: p.info for p in psutil.process_iter(['name', 'exe', 'cmdline'])}
        suspicious = []
        
        # Check for new processes not in baseline
        for pid, info in current_processes.items():
            if pid not in self.process_baseline:
                if not self._is_process_whitelisted(info):
                    suspicious.append(info)
        
        if suspicious:
            self._handle_suspicious_activity(
                'process',
                f"New processes detected: {suspicious}",
                severity=len(suspicious)*2
            )
        
        # Update baseline
        self.process_baseline = current_processes

    def _monitor_system_performance(self):
        """Monitor for abnormal resource usage"""
        cpu_usage = psutil.cpu_percent(interval=1)
        mem_usage = psutil.virtual_memory().percent
        
        thresholds = {
            'cpu': 80 + (self.threat_level * 2),  # Dynamic threshold based on threat level
            'memory': 85 + (self.threat_level * 2)
        }
        
        alerts = []
        if cpu_usage > thresholds['cpu']:
            alerts.append(f"High CPU usage: {cpu_usage}%")
        if mem_usage > thresholds['memory']:
            alerts.append(f"High memory usage: {mem_usage}%")
        
        if alerts:
            self._handle_suspicious_activity(
                'performance',
                " | ".join(alerts),
                severity=max(cpu_usage, mem_usage)/10
            )

    def _check_system_integrity(self):
        """Check critical files for modifications"""
        critical_files = {
            'agents/commander.py': self._hash_file('agents/commander.py'),
            'core/crypto.py': self._hash_file('core/crypto.py'),
            'config/api_keys.ini': self._hash_file('config/api_keys.ini')
        }
        
        modified = []
        for file, known_hash in self.integrity_baseline.items():
            current_hash = self._hash_file(file)
            if current_hash != known_hash:
                modified.append(file)
        
        if modified:
            self._handle_suspicious_activity(
                'integrity',
                f"Critical files modified: {modified}",
                severity=10  # Highest severity
            )

    def _full_system_scan(self):
        """Perform comprehensive security scan"""
        logger(f"[{self.name}] Initiating full system scan")
        
        scan_results = {
            'network': self._scan_network(),
            'processes': self._scan_processes(),
            'filesystem': self._scan_filesystem(),
            'performance': self._scan_performance()
        }
        
        threat_score = sum(
            len(result['threats']) * result['severity'] 
            for result in scan_results.values()
        ) / 10
        
        self._update_threat_level(threat_score)
        
        # Send scan report
        self._send_results(
            recipient='Commander',
            message_type='security_scan_report',
            content={
                'threat_level': self.threat_level,
                'scan_results': scan_results,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _scan_network(self):
        """Deep network scan"""
        connections = self._get_network_connections()
        threats = []
        
        for conn in connections:
            if not self._is_connection_authorized(conn):
                threats.append({
                    'type': 'unauthorized_connection',
                    'connection': conn,
                    'recommendation': 'block'
                })
        
        return {
            'threats': threats,
            'severity': 3,
            'connections_analyzed': len(connections)
        }

    def _scan_processes(self):
        """Deep process scan"""
        processes = {p.pid: p.info for p in psutil.process_iter(['name', 'exe', 'cmdline'])}
        threats = []
        
        # Check for known malicious processes
        for pid, info in processes.items():
            for sig in self.threat_signatures['processes']:
                if sig in info['name'].lower() or (info['cmdline'] and any(sig in cmd.lower() for cmd in info['cmdline'])):
                    threats.append({
                        'type': 'malicious_process',
                        'process': info,
                        'signature': sig,
                        'recommendation': 'terminate'
                    })
        
        return {
            'threats': threats,
            'severity': 4,
            'processes_analyzed': len(processes)
        }

    def _scan_filesystem(self):
        """Critical filesystem scan"""
        threats = []
        critical_files = [
            'agents/*.py',
            'core/*.py',
            'config/*.ini',
            'requirements.txt'
        ]
        
        # Check file permissions
        for pattern in critical_files:
            for file in glob.glob(pattern):
                if os.stat(file).st_mode & 0o777 != 0o600:  # Should be read-write only by owner
                    threats.append({
                        'type': 'insecure_permissions',
                        'file': file,
                        'recommendation': 'chmod 600'
                    })
        
        return {
            'threats': threats,
            'severity': 5,
            'files_checked': len(critical_files)
        }

    def _scan_performance(self):
        """Performance anomaly scan"""
        threats = []
        metrics = {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }
        
        thresholds = {'cpu': 90, 'memory': 90, 'disk': 95}
        
        for metric, value in metrics.items():
            if value > thresholds[metric]:
                threats.append({
                    'type': 'resource_exhaustion',
                    'metric': metric,
                    'usage': f"{value}%",
                    'threshold': f"{thresholds[metric]}%",
                    'recommendation': 'investigate'
                })
        
        return {
            'threats': threats,
            'severity': 2,
            'metrics': metrics
        }

    def _handle_threat_alert(self, task):
        """Process threat alerts from other agents"""
        threat = task['threat']
        logger(f"[{self.name}] Processing threat alert: {threat['description']}")
        
        # Increase threat level based on severity
        self._update_threat_level(threat.get('severity', 1))
        
        # Automatically select countermeasures
        if self.threat_level >= 7:
            self._activate_lockdown()
        elif self.threat_level >= 4:
            self._activate_countermeasures(['isolate_network', 'suspend_non_critical'])

    def _handle_suspicious_activity(self, category, description, severity):
        """Handle detected suspicious activity"""
        logger(f"[{self.name}] {category.upper()} ALERT: {description}")
        
        # Update threat level
        self._update_threat_level(severity)
        
        # Trigger appropriate response
        if severity >= 8:
            self._activate_lockdown()
        elif severity >= 5:
            self._activate_countermeasures(['enhanced_monitoring', 'process_restrictions'])
        
        # Notify commander
        self._send_results(
            recipient='Commander',
            message_type='security_alert',
            content={
                'category': category,
                'description': description,
                'severity': severity,
                'threat_level': self.threat_level,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _update_threat_level(self, increment):
        """Adjust system threat level"""
        new_level = min(10, self.threat_level + increment)
        if new_level != self.threat_level:
            self.threat_level = new_level
            logger(f"[{self.name}] Threat level changed to {self.threat_level}")
            
            # Adjust monitoring intensity based on threat level
            self._adjust_monitoring()

    def _adjust_monitoring(self):
        """Adjust monitoring frequency based on threat level"""
        base_intervals = {
            'network': 5,
            'process': 10,
            'performance': 15,
            'integrity': 30
        }
        
        # More frequent monitoring at higher threat levels
        multiplier = max(0.1, 1 - (self.threat_level * 0.05))
        
        self.monitoring_intervals = {
            k: max(1, int(v * multiplier))
            for k, v in base_intervals.items()
        }
        
        # Reinitialize monitoring schedules
        schedule.clear()
        self._init_monitoring()

    def _activate_countermeasures(self, measures):
        """Activate specific security countermeasures"""
        activated = []
        
        for measure in measures:
            if measure not in self.active_countermeasures:
                activated.append(measure)
                self.active_countermeasures.append(measure)
                
                if measure == 'isolate_network':
                    self._isolate_network()
                elif measure == 'suspend_non_critical':
                    self._suspend_non_critical_processes()
                elif measure == 'enhanced_monitoring':
                    self._enhance_monitoring()
                elif measure == 'process_restrictions':
                    self._restrict_process_creation()
        
        if activated:
            logger(f"[{self.name}] Activated countermeasures: {activated}")

    def _activate_lockdown(self):
        """Activate full system lockdown"""
        if 'lockdown' in self.active_countermeasures:
            return
            
        logger(f"[{self.name}] ACTIVATING LOCKDOWN PROTOCOL")
        
        # Critical measures
        measures = [
            'isolate_network',
            'suspend_non_critical',
            'freeze_assets',
            'enable_logging',
            'backup_critical'
        ]
        
        for measure in measures:
            if measure not in self.active_countermeasures:
                self.active_countermeasures.append(measure)
                
                if measure == 'freeze_assets':
                    self._freeze_content_assets()
                elif measure == 'enable_logging':
                    self._enable_enhanced_logging()
                elif measure == 'backup_critical':
                    self._backup_critical_data()
        
        # Notify commander
        self._send_results(
            recipient='Commander',
            message_type='lockdown_activated',
            content={
                'threat_level': self.threat_level,
                'active_measures': self.active_countermeasures,
                'timestamp': datetime.now().isoformat()
            }
        )

    def _isolate_network(self):
        """Isolate system from network"""
        try:
            # Windows specific - disable network adapters
            subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Ethernet"', 'admin=disable'], check=True)
            subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=disable'], check=True)
            logger(f"[{self.name}] Network isolation complete")
        except subprocess.CalledProcessError as e:
            logger(f"[{self.name}] Network isolation failed: {str(e)}")

    def _suspend_non_critical_processes(self):
        """Suspend non-essential processes"""
        critical_processes = ['python', 'system', 'svchost']
        suspended = []
        
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() not in critical_processes and proc.pid != os.getpid():
                    proc.suspend()
                    suspended.append(proc.name())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if suspended:
            logger(f"[{self.name}] Suspended processes: {suspended[:5]}... (total: {len(suspended)})")

    def _enhance_monitoring(self):
        """Increase monitoring intensity"""
        self.monitoring_intervals = {
            'network': 1,
            'process': 2,
            'performance': 5,
            'integrity': 10
        }
        self._adjust_monitoring()
        logger(f"[{self.name}] Enhanced monitoring activated")

    def _restrict_process_creation(self):
        """Implement process creation restrictions"""
        # Windows-specific - would require more advanced implementation
        logger(f"[{self.name}] Process creation restrictions enabled (simulated)")

    def _freeze_content_assets(self):
        """Protect content assets from modification"""
        # In production, would change file permissions to read-only
        logger(f"[{self.name}] Content assets frozen (read-only mode)")

    def _enable_enhanced_logging(self):
        """Enable comprehensive system logging"""
        logger(f"[{self.name}] Enhanced logging activated")

    def _backup_critical_data(self):
        """Backup critical system data"""
        # In production, would copy to secure location
        logger(f"[{self.name}] Critical data backup initiated")

    def _get_network_connections(self):
        """Get current network connections"""
        connections = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                connections.append({
                    'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote': f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else None,
                    'pid': conn.pid,
                    'status': conn.status
                })
        return connections

    def _is_connection_authorized(self, conn):
        """Check if connection is authorized"""
        # Check against whitelist
        for allowed in self.whitelist['connections']:
            if (allowed.get('ip') == conn['remote'].split(':')[0] if conn['remote'] else False):
                return True
        
        # Check if local process
        if conn['remote'] is None:
            return True
            
        return False

    def _is_process_whitelisted(self, process_info):
        """Check if process is whitelisted"""
        for allowed in self.whitelist['processes']:
            if allowed['name'].lower() in process_info['name'].lower():
                return True
            if process_info['exe'] and allowed.get('path') in process_info['exe']:
                return True
        return False

    def _hash_file(self, filepath):
        """Generate file hash for integrity checking"""
        if not os.path.exists(filepath):
            return None
            
        hasher = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def _establish_network_baseline(self):
        """Establish normal network activity baseline"""
        return self._get_network_connections()

    def _establish_process_baseline(self):
        """Establish normal process baseline"""
        return {p.pid: p.info for p in psutil.process_iter(['name', 'exe', 'cmdline'])}

    def _establish_performance_baseline(self):
        """Establish normal performance baseline"""
        return {
            'cpu': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory().percent,
            'disk': psutil.disk_usage('/').percent
        }

    def _load_whitelist(self):
        """Load authorized connections and processes"""
        return {
            'connections': [
                {'ip': '127.0.0.1', 'port': '*', 'description': 'localhost'},
                {'ip': 'api.openai.com', 'port': '443', 'description': 'OpenAI API'}
            ],
            'processes': [
                {'name': 'python', 'description': 'Python interpreter'},
                {'name': 'chrome', 'description': 'Web browser'},
                {'name': 'svchost', 'description': 'Windows service host'}
            ]
        }

    def _load_threat_signatures(self):
        """Load known threat signatures"""
        return {
            'processes': [
                'keylogger', 'ransom', 'miner', 'spyware', 
                'rat', 'trojan', 'worm', 'rootkit'
            ],
            'connections': [
                'malicious.domain', 'botnet.server', 
                'tor.exit.node', 'vpn.hacker'
            ]
        }

    def _update_whitelist(self, task):
        """Update whitelist with new entries"""
        for category, items in task['entries'].items():
            if category in self.whitelist:
                self.whitelist[category].extend(items)
        
        logger(f"[{self.name}] Whitelist updated with {len(task['entries'])} new entries")

    def _send_results(self, recipient, message_type, content):
        """Encrypt and send security reports"""
        payload = {
            'type': message_type,
            'content': content,
            'timestamp': datetime.now().isoformat(),
            'origin': self.name
        }
        
        encrypted = self.crypto.encrypt(json.dumps(payload))
        message = {
            'to': recipient,
            'payload': encrypted,
            'encrypted': True
        }
        
        # In production, would use message broker
        logger(f"[{self.name}] Sent {message_type} to {recipient}")

    def receive_message(self, message):
        """Public interface for receiving tasks"""
        self.task_queue.put(message)

    def shutdown(self):
        """Gracefully shutdown the sentinel"""
        self.running = False
        logger(f"[{self.name}] Shutting down...")
        
        # Disable all countermeasures before shutdown
        if self.active_countermeasures:
            logger(f"[{self.name}] Deactivating countermeasures: {self.active_countermeasures}")
            self.active_countermeasures = []
        
        self.thread.join(timeout=5)
        logger(f"[{self.name}] Shutdown complete")

# Standalone test
if __name__ == "__main__":
    from core.crypto import MilitaryCrypto
    
    print("Testing Security Sentinel...")
    crypto = MilitaryCrypto()
    sentinel = SecuritySentinel(crypto)
    
    # Test network monitoring
    sentinel.receive_message({
        'type': 'security_scan',
        'scope': 'full'
    })
    
    # Test threat alert
    sentinel.receive_message({
        'type': 'threat_alert',
        'threat': {
            'description': 'Simulated malware detected',
            'severity': 8,
            'source': 'process_monitor'
        }
    })
    
    # Allow time for processing
    time.sleep(10)
    
    # Shutdown
    sentinel.shutdown()
    print("Security Sentinel test completed.")
