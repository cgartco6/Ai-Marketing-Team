import os
import json
import logging
import hashlib
import base64
from datetime import datetime
import configparser
from typing import Dict, Any, Optional
import socket
import psutil
import numpy as np
from cryptography.fernet import Fernet
import pickle
import inspect
import threading
import queue

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
    handlers=[
        logging.FileHandler('ai_team.log'),
        logging.StreamHandler()
    ]
)

def logger(message: str, level: str = 'info') -> None:
    """Enhanced logging utility with level-based formatting"""
    log_levels = {
        'debug': logging.debug,
        'info': logging.info,
        'warning': logging.warning,
        'error': logging.error,
        'critical': logging.critical
    }
    
    # Get the caller's information
    caller_frame = inspect.stack()[1]
    caller_module = inspect.getmodule(caller_frame[0]).__name__ if inspect.getmodule(caller_frame[0]) else 'unknown'
    caller_name = caller_frame[3]
    
    # Format the message with caller info
    formatted_msg = f"[{caller_module}.{caller_name}] {message}"
    
    # Log the message
    log_func = log_levels.get(level.lower(), logging.info)
    log_func(formatted_msg)

def secure_fetch(key_name: str, config_file: str = 'config/api_keys.ini') -> str:
    """Securely fetch API keys with error handling"""
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if not config.has_option('API_KEYS', key_name):
            logger(f"API key '{key_name}' not found in config", 'error')
            raise ValueError(f"API key '{key_name}' not configured")
        
        return config['API_KEYS'][key_name]
    except Exception as e:
        logger(f"Failed to fetch API key '{key_name}': {str(e)}", 'error')
        raise

def generate_fernet_key() -> str:
    """Generate a new Fernet encryption key"""
    return Fernet.generate_key().decode()

def hash_data(data: str, algorithm: str = 'sha256') -> str:
    """Generate cryptographic hash of data"""
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()

def object_to_bytes(obj: Any) -> bytes:
    """Serialize Python object to bytes"""
    return pickle.dumps(obj)

def bytes_to_object(data: bytes) -> Any:
    """Deserialize bytes to Python object"""
    return pickle.loads(data)

def encode_base64(data: bytes) -> str:
    """Encode binary data to base64 string"""
    return base64.b64encode(data).decode('utf-8')

def decode_base64(data: str) -> bytes:
    """Decode base64 string to binary data"""
    return base64.b64decode(data.encode('utf-8'))

def get_system_info() -> Dict[str, Any]:
    """Collect system information for diagnostics"""
    return {
        'timestamp': datetime.now().isoformat(),
        'hostname': socket.gethostname(),
        'os': os.name,
        'platform': os.uname().system if hasattr(os, 'uname') else 'Windows',
        'cpu_usage': psutil.cpu_percent(interval=1),
        'memory': psutil.virtual_memory()._asdict(),
        'disk': psutil.disk_usage('/')._asdict(),
        'network': {
            'connections': len(psutil.net_connections()),
            'bytes_sent': psutil.net_io_counters().bytes_sent,
            'bytes_recv': psutil.net_io_counters().bytes_recv
        },
        'process_count': len(psutil.pids())
    }

class ThreadSafeQueue:
    """Thread-safe queue implementation with enhanced features"""
    def __init__(self, maxsize: int = 0):
        self.queue = queue.Queue(maxsize=maxsize)
        self.lock = threading.Lock()
        
    def put(self, item: Any, block: bool = True, timeout: Optional[float] = None) -> None:
        with self.lock:
            self.queue.put(item, block, timeout)
            
    def get(self, block: bool = True, timeout: Optional[float] = None) -> Any:
        with self.lock:
            return self.queue.get(block, timeout)
            
    def qsize(self) -> int:
        with self.lock:
            return self.queue.qsize()
            
    def empty(self) -> bool:
        with self.lock:
            return self.queue.empty()
            
    def full(self) -> bool:
        with self.lock:
            return self.queue.full()
            
    def clear(self) -> None:
        with self.lock:
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                except queue.Empty:
                    continue

class RateLimiter:
    """API rate limiting utility"""
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.timestamps = []
        self.lock = threading.Lock()
        
    def __call__(self) -> bool:
        with self.lock:
            now = time.time()
            # Remove old timestamps
            self.timestamps = [t for t in self.timestamps if now - t < self.period]
            
            if len(self.timestamps) >= self.max_calls:
                return False
                
            self.timestamps.append(now)
            return True

class PerformanceTimer:
    """Context manager for performance timing"""
    def __init__(self, name: str = ''):
        self.name = name
        self.start_time = None
        self.end_time = None
        
    def __enter__(self):
        self.start_time = time.perf_counter()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.perf_counter()
        elapsed = self.end_time - self.start_time
        logger(f"{self.name} executed in {elapsed:.4f} seconds", 'debug')
        
    def elapsed(self) -> float:
        if self.start_time is None:
            return 0.0
        end = self.end_time or time.perf_counter()
        return end - self.start_time

class DataSanitizer:
    """Data sanitization and validation utilities"""
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """Sanitize potentially dangerous strings"""
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")
            
        sanitized = input_str.strip()
        sanitized = sanitized.replace('\0', '')  # Remove null bytes
        sanitized = sanitized[:max_length]  # Enforce max length
        
        return sanitized
        
    @staticmethod
    def validate_email(email: str) -> bool:
        """Basic email validation"""
        if not isinstance(email, str):
            return False
            
        return '@' in email and '.' in email.split('@')[-1]
        
    @staticmethod
    def clean_dict(input_dict: Dict) -> Dict:
        """Remove None values from dictionary"""
        return {k: v for k, v in input_dict.items() if v is not None}

class FileLock:
    """Simple file-based locking mechanism"""
    def __init__(self, lockfile: str):
        self.lockfile = lockfile
        self.locked = False
        
    def acquire(self) -> bool:
        """Acquire the lock"""
        try:
            if os.path.exists(self.lockfile):
                return False
                
            with open(self.lockfile, 'w') as f:
                f.write(str(os.getpid()))
            self.locked = True
            return True
        except:
            return False
            
    def release(self) -> None:
        """Release the lock"""
        if self.locked and os.path.exists(self.lockfile):
            os.remove(self.lockfile)
            self.locked = False
            
    def __enter__(self):
        self.acquire()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

class CircularBuffer:
    """Fixed-size circular buffer implementation"""
    def __init__(self, size: int):
        self.size = size
        self.buffer = []
        self.index = 0
        
    def add(self, item: Any) -> None:
        """Add an item to the buffer"""
        if len(self.buffer) < self.size:
            self.buffer.append(item)
        else:
            self.buffer[self.index] = item
        self.index = (self.index + 1) % self.size
        
    def get_all(self) -> list:
        """Get all items in the buffer"""
        return self.buffer[self.index:] + self.buffer[:self.index]
        
    def clear(self) -> None:
        """Clear the buffer"""
        self.buffer = []
        self.index = 0

def setup_directories() -> None:
    """Ensure required directories exist"""
    dirs = [
        'data',
        'data/campaigns',
        'data/analytics',
        'assets',
        'assets/templates',
        'assets/output',
        'logs'
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    logger("Verified directory structure")

def validate_config(config_path: str = 'config/settings.ini') -> bool:
    """Validate the configuration file"""
    required_sections = {
        'API_KEYS': ['OPENAI_API_KEY'],
        'PERFORMANCE': ['MAX_CONCURRENT_CAMPAIGNS'],
        'SECURITY': ['ENCRYPTION_KEY']
    }
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        
        for section, keys in required_sections.items():
            if not config.has_section(section):
                logger(f"Missing config section: {section}", 'error')
                return False
                
            for key in keys:
                if not config.has_option(section, key):
                    logger(f"Missing config key: {section}.{key}", 'error')
                    return False
                    
        return True
    except Exception as e:
        logger(f"Config validation failed: {str(e)}", 'error')
        return False

def ooda_cycle(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Implement OODA loop (Observe-Orient-Decide-Act) for decision making
    
    Args:
        data: Input data containing 'situation' and 'objectives'
    
    Returns:
        Dict with 'observation', 'orientation', 'decision', and 'action'
    """
    result = {
        'observation': None,
        'orientation': None,
        'decision': None,
        'action': None,
        'timestamp': datetime.now().isoformat()
    }
    
    try:
        # Observe
        result['observation'] = {
            'current_state': data.get('situation'),
            'environmental_factors': data.get('environment', {})
        }
        
        # Orient
        result['orientation'] = {
            'analysis': _analyze_situation(result['observation']),
            'options': _generate_options(data.get('objectives'))
        }
        
        # Decide
        result['decision'] = _select_best_option(
            result['orientation']['options'],
            data.get('constraints', {})
        )
        
        # Act
        result['action'] = {
            'steps': _create_action_plan(result['decision']),
            'resources': _allocate_resources(result['decision'])
        }
        
    except Exception as e:
        logger(f"OODA cycle failed: {str(e)}", 'error')
        result['error'] = str(e)
        
    return result

def _analyze_situation(observation: Dict) -> Dict:
    """Internal: Analyze the current situation"""
    return {
        'strengths': [],
        'weaknesses': [],
        'opportunities': [],
        'threats': []
    }

def _generate_options(objectives: Dict) -> List[Dict]:
    """Internal: Generate possible options"""
    return [{
        'id': f"opt_{hash_data(str(objectives))[:8]}",
        'description': "Default option",
        'expected_outcome': "Achieve objectives",
        'resource_requirements': {}
    }]

def _select_best_option(options: List[Dict], constraints: Dict) -> Dict:
    """Internal: Select the best option"""
    return options[0] if options else {}

def _create_action_plan(decision: Dict) -> List[Dict]:
    """Internal: Create action steps"""
    return [{
        'step': 1,
        'action': 'Implement decision',
        'owner': 'System',
        'deadline': (datetime.now() + timedelta(hours=1)).isoformat()
    }]

def _allocate_resources(decision: Dict) -> Dict:
    """Internal: Allocate resources"""
    return {
        'time': 60,
        'budget': 100,
        'personnel': 1
    }

if __name__ == "__main__":
    # Test utility functions
    print("Testing utils module...")
    
    # Test logging
    logger("This is a test message", "info")
    
    # Test hashing
    test_data = "secret_data"
    hashed = hash_data(test_data)
    print(f"Hashed data: {hashed}")
    
    # Test system info
    sys_info = get_system_info()
    print(f"System info: {json.dumps(sys_info, indent=2)}")
    
    # Test OODA cycle
    ooda_result = ooda_cycle({
        'situation': 'New product launch',
        'objectives': ['maximize reach', 'increase engagement']
    })
    print(f"OODA result: {json.dumps(ooda_result, indent=2)}")
    
    print("Utils module tests completed.")
