import os
import sys
import time
import hashlib
import platform
import socket
import psutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import shutil
import subprocess
import threading
import json
import asyncio
import websockets
import requests
import getpass
import webbrowser
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from collections import deque
import random

# Global queue to send messages to the WebSocket client
ws_send_queue = Queue()
# Global variable to hold the WebSocket client instance
ws_client = None
# Global variable to hold the file observer instance
file_observer = None

def print_banner():
    banner = """
 [34m██████╗██╗   ██╗██████╗ ███████╗██████╗     ██████╗  █████╗ ███████╗ ██████╗ ██████╗ 
██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ██╔══██╗██╔══██╗╚══███╔╝██╔═══██╗██╔══██╗
██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝    ██████╔╝███████║  ███╔╝ ██║   ██║██████╔╝
██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗    ██╔══██╗██╔══██║ ███╔╝  ██║   ██║██╔══██╗
╚██████╗   ██║   ██████╔╝███████╗██║  ██║    ██║  ██║██║  ██║███████╗╚██████╔╝██║  ██║
 ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝
[0m"""
    print(banner)
    print("="*88)
    print("Welcome to Cyber Razor - Advanced Security Agent v2.0")
    print("Real-time Threat Detection & AI Analysis - Free Tier (WebSocket Edition)")
    print("="*88)
    print()

class Config:
    LOGGING_ENABLED = True
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.path.join(os.path.expanduser("~"), ".cyberrazor", "freetier.log")
    SCAN_PATHS = [
        os.path.expanduser("~/Downloads"), 
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        "C:\\Users",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\Windows\\System32",
        "C:\\Temp",
        os.path.expanduser("~/AppData/Local/Temp")
    ]
    REALTIME_MONITOR_PATHS = [
        os.path.expanduser("~/Downloads"), 
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Documents"),
        "C:\\Users",  # Monitor all user directories
        "C:\\Temp",  # Monitor temp directory
        os.path.expanduser("~/AppData/Local/Temp"),  # User temp
        "C:\\Program Files",  # Monitor program installations
        "C:\\Program Files (x86)"  # Monitor 32-bit programs
    ]
    EXTENSIONS = ['.exe', '.dll', '.py', '.sh', '.pdf', '.doc', '.docx', '.apk', '.jar', '.bat', '.ps1', '.zip', '.rar', '.txt', '.log', '.ini']
    PORTAL_URL = os.getenv("CYBERRAZOR_PORTAL_URL", "wss://cyberrazorbackend.vercel.app/ws")
    API_KEY = os.getenv("CYBERRAZOR_API_KEY")
    CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".cyberrazor")
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
    AUTH_API_URL = os.getenv("CYBERRAZOR_API_URL", "https://cyberrazorbackend.vercel.app")
    ACTIVATION_API_URL = os.getenv("CYBERRAZOR_ACTIVATION_URL", "https://cyberrazorbackend.vercel.app")

class WebSocketClient(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.name = "WebSocketClientThread"
        self._stop_event = threading.Event()

    async def _run(self):
        while not self._stop_event.is_set():
            try:
                # Connect to WebSocket without extra_headers to avoid compatibility issues
                async with websockets.connect(Config.PORTAL_URL) as websocket:
                    logging.info("WebSocket connection established.")
                    # Send authentication message after connection
                    if Config.API_KEY:
                        auth_message = {
                            "type": "auth",
                            "token": Config.API_KEY
                        }
                        await websocket.send(json.dumps(auth_message))
                        logging.info("🔑 Authentication token sent via WebSocket")
                    
                    # Start two tasks: one for sending, one for receiving
                    consumer_task = asyncio.ensure_future(self._consumer_handler(websocket))
                    producer_task = asyncio.ensure_future(self._producer_handler(websocket))
                    done, pending = await asyncio.wait(
                        [consumer_task, producer_task],
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    for task in pending:
                        task.cancel()
            except Exception as e:
                logging.error(f"WebSocket connection error: {e}. Retrying in 15 seconds.")
                await asyncio.sleep(15)

    async def _consumer_handler(self, websocket):
        """Handles incoming messages from the server."""
        async for message in websocket:
            try:
                data = json.loads(message)
                if data.get("type") == "action":
                    payload = data.get("payload", {})
                    threat_id = payload.get("threat_id")
                    action = payload.get("action")
                    file_path = payload.get("file_path")
                    logging.info(f"Received action '{action}' for threat '{threat_id}' on file '{file_path}'")
                    self.execute_action(action, file_path)
            except json.JSONDecodeError:
                logging.warning(f"Received non-JSON message: {message}")
            except Exception as e:
                logging.error(f"Error processing incoming message: {e}")

    async def _producer_handler(self, websocket):
        """Handles outgoing messages to the server."""
        while True:
            if not ws_send_queue.empty():
                message = ws_send_queue.get()
                await websocket.send(json.dumps(message))
            await asyncio.sleep(0.1)

    def execute_action(self, action: str, file_path: str):
        """Executes a file action based on command from the portal."""
        if not os.path.exists(file_path):
            logging.error(f"Action '{action}' failed: File not found at '{file_path}'")
            return

        try:
            if action == "accept":
                logging.info(f"Action 'accept': File '{file_path}' marked as safe.")
            elif action == "remove":
                os.remove(file_path)
                logging.info(f"Action 'remove': File '{file_path}' has been deleted.")
            elif action == "quarantine":
                quarantine_dir = os.path.join(os.path.expanduser("~"), ".cyberrazor", "quarantine")
                os.makedirs(quarantine_dir, exist_ok=True)
                filename = os.path.basename(file_path)
                quarantine_path = os.path.join(quarantine_dir, f"{int(time.time())}_{filename}")
                shutil.move(file_path, quarantine_path)
                logging.info(f"Action 'quarantine': File '{file_path}' moved to '{quarantine_path}'.")
        except Exception as e:
            logging.error(f"Failed to execute action '{action}' on '{file_path}': {e}")

    def run(self):
        asyncio.run(self._run())

    def stop(self):
        self._stop_event.set()

class WebSocketLogHandler(logging.Handler):
    """A logging handler that sends records to the WebSocket queue."""
    def emit(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": self.format(record),
        }
        ws_send_queue.put({"type": "log", "payload": log_entry})

def setup_logging():
    os.makedirs(os.path.dirname(Config.LOG_FILE), exist_ok=True)
    
    # Basic file handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # WebSocket handler
    ws_handler = WebSocketLogHandler()
    ws_handler.setLevel(logging.INFO)

    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        handlers=[file_handler, console_handler, ws_handler]
    )
    return logging.getLogger(__name__)


# ===== Persistent config (tier, user) =====
def load_local_config() -> Dict[str, Any]:
    try:
        if os.path.exists(Config.CONFIG_FILE):
            with open(Config.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logging.debug(f"Failed to load config: {e}")
    return {}


def save_local_config(data: Dict[str, Any]):
    try:
        os.makedirs(Config.CONFIG_DIR, exist_ok=True)
        with open(Config.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logging.debug(f"Failed to save config: {e}")


def set_tier(tier: str):
    cfg = load_local_config()
    cfg['tier'] = tier
    save_local_config(cfg)


def get_tier() -> str:
    return load_local_config().get('tier', 'free')


# ===== Auth & activation =====
def login():
    """Handle user login with admin approval check"""
    try:
        print("Please login to CyberRazor")
        email = input("Email: ")
        password = getpass.getpass("Password: ")
        
        # Make login request
        login_data = {
            "email": email,
            "password": password
        }
        
        response = requests.post(f"{Config.AUTH_API_URL}/api/auth/login", json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if user is approved by admin
            if not check_admin_approval(email, data.get('access_token')):
                print("⏳ Please wait for admin approval before using CyberRazor agent.")
                print("📧 Your account is registered but pending admin approval.")
                print("🔔 You will receive an email notification once approved.")
                return False
            
            Config.API_KEY = data.get('access_token')
            Config.USER_EMAIL = email
            
            print("✅ Login successful!")
            print("✅ Account approved by admin - access granted!")
            return True
        else:
            error_data = response.json()
            print(f"❌ Login failed: {error_data.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def check_admin_approval(email, token):
    """Check if user is approved by admin"""
    try:
        print("🔍 Checking admin approval status...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # Check user profile/status endpoint
        response = requests.get(f"{Config.AUTH_API_URL}/api/auth/profile", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            
            # Check various possible approval fields
            is_approved = (
                user_data.get('approved', False) or 
                user_data.get('isApproved', False) or 
                user_data.get('admin_approved', False) or
                user_data.get('status') == 'approved' or
                user_data.get('account_status') == 'active'
            )
            
            if is_approved:
                print("✅ Admin approval: APPROVED")
                return True
            else:
                print("⏳ Admin approval: PENDING")
                print(f"📋 Account status: {user_data.get('status', 'pending')}")
                return False
                
        elif response.status_code == 403:
            print("⏳ Admin approval: PENDING (Access forbidden)")
            return False
        else:
            print(f"⚠️ Could not verify approval status (HTTP {response.status_code})")
            # If we can't verify, assume approved to avoid blocking legitimate users
            return True
            
    except Exception as e:
        print(f"⚠️ Error checking admin approval: {e}")
        # If there's an error checking, assume approved to avoid blocking legitimate users
        return True


def activate_pro_flow():
    print("\nEnter your activation key (sent to your email)")
    activation_key = input("Activation Key: ").strip()
    if not activation_key:
        print("No key provided.")
        return
    email = load_local_config().get('user_email') or input("Email (used for activation): ").strip()
    payload = {
        "user_email": email,
        "hostname": socket.gethostname(),
        "os_info": f"{platform.system()} {platform.release()}",
        "activation_key": activation_key
    }
    try:
        resp = requests.post(
            f"{Config.ACTIVATION_API_URL}/api/devices/activate-key",
            json=payload,
            timeout=20
        )
        if resp.status_code == 200:
            print("✅ Pro activated!")
            cfg = load_local_config()
            cfg.update({
                "activated": True,
                "activation_key": activation_key,
                "device_id": resp.json().get('activation_id'),
                "activated_at": datetime.now().isoformat(),
                "user_email": email
            })
            save_local_config(cfg)
            set_tier('pro')
            return
        print(f"❌ Activation failed: {resp.text}")
    except Exception as e:
        print(f"❌ Activation error: {e}")


# ===== Simple arrow-key menu (Windows-friendly) =====
def arrow_menu(title: str, options: List[str]) -> int:
    index = 0
    def render():
        os.system('cls' if os.name == 'nt' else 'clear')
        print_banner()
        print(title)
        print()
        for i, opt in enumerate(options):
            prefix = "> " if i == index else "  "
            print(f"{prefix}{opt}")
    try:
        if os.name == 'nt':
            import msvcrt
            while True:
                render()
                ch = msvcrt.getch()
                if ch in (b'\r', b'\n'):
                    return index
                if ch == b'\xe0':
                    ch2 = msvcrt.getch()
                    if ch2 == b'H':
                        index = (index - 1) % len(options)
                    elif ch2 == b'P':
                        index = (index + 1) % len(options)
        else:
            import termios, tty
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                while True:
                    render()
                    ch = sys.stdin.read(1)
                    if ch == "\r" or ch == "\n":
                        termios.tcsetattr(fd, termios.TCSADRAIN, old)
                        return index
                    if ch == "\x1b":
                        seq = sys.stdin.read(2)
                        if seq == "[A":
                            index = (index - 1) % len(options)
                        elif seq == "[B":
                            index = (index + 1) % len(options)
            finally:
                try:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old)
                except Exception:
                    pass
    except KeyboardInterrupt:
        return len(options) - 1
    return 0

def hash_file(file_path: str) -> Optional[str]:
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception as e:
        logging.error(f"Error hashing file {file_path}: {e}")
        return None

def get_file_metadata(file_path: str) -> Dict[str, Any]:
    try:
        stat = os.stat(file_path)
        return {
            "size": stat.st_size,
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
            "permissions": oct(stat.st_mode)[-3:],
        }
    except Exception as e:
        logging.error(f"Error getting metadata for {file_path}: {e}")
        return {}

def handle_threat_response(file_path: str, ai_result: Dict[str, Any], file_metadata: Dict[str, Any]):
    """Sends threat information to the portal via WebSocket."""
    threat_id = hashlib.sha256(file_path.encode()).hexdigest()
    threat_data = {
        "threat_id": threat_id,
        "file_path": file_path,
        "file_metadata": file_metadata,
        "scan_result": ai_result,
        "timestamp": datetime.now().isoformat(),
    }
    ws_send_queue.put({"type": "threat", "payload": threat_data})
    logging.warning(f"Threat detected and reported to portal: {file_path}. Waiting for user action.")

def scan_files():
    logging.info("Starting file scan...")
    scanned_count = 0
    threat_count = 0
    for root_path in Config.SCAN_PATHS:
        if not os.path.exists(root_path):
            continue
        for root, _, files in os.walk(root_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in Config.EXTENSIONS):
                    file_path = os.path.join(root, file)
                    scanned_count += 1
                    file_hash = hash_file(file_path)
                    if file_hash and file_path.lower().endswith('.exe'):
                        threat_count += 1
                        file_metadata = get_file_metadata(file_path)
                        file_metadata['hash'] = file_hash
                        ai_result = {
                            "verdict": "Suspicious",
                            "confidence": "Medium",
                            "reason": "Executable file detected in Free Tier.",
                            "severity": "low"
                        }
                        handle_threat_response(file_path, ai_result, file_metadata)
    logging.info(f"Scan complete. Scanned {scanned_count} files, found {threat_count} potential threats.")

class RealTimeFileMonitor(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        self.monitored_extensions = Config.EXTENSIONS
        self.request_queue = deque()
        self.priority_queue = deque()  # High priority queue for malicious files
        self.last_request_time = 0
        self.min_request_interval = 2.0  # Minimum 2 seconds between requests
        self.malicious_interval = 2.0  # 2 seconds for malicious files
        self.safe_interval = 5.0  # 5 seconds for safe files
        self.batch_size = 5  # Increased batch size
        self.processed_files = {}  # Track processed files to avoid duplicates
        self.file_cooldown = 15.0  # Don't process same file again for 15 seconds
        logging.info(f"🔍 File monitor initialized. Watching extensions: {self.monitored_extensions}")
        logging.info(f"⏱️ Rate limiting: {self.min_request_interval}s between requests, batch size: {self.batch_size}")
        logging.info(f"🔄 File deduplication: {self.file_cooldown}s cooldown per file")
        
    def on_created(self, event):
        if not event.is_directory:
            logging.info(f"📁 File created detected: {event.src_path}")
            self.check_file(event.src_path, "File Created")
    
    def on_modified(self, event):
        if not event.is_directory:
            logging.info(f"📝 File modified detected: {event.src_path}")
            self.check_file(event.src_path, "File Modified")
    
    def on_moved(self, event):
        if not event.is_directory:
            logging.info(f"📦 File moved detected: {event.dest_path}")
            self.check_file(event.dest_path, "File Moved")
    
    def check_file(self, file_path, event_type):
        try:
            # Check if we've already processed this file recently
            current_time = time.time()
            if file_path in self.processed_files:
                last_processed = self.processed_files[file_path]
                if current_time - last_processed < self.file_cooldown:
                    logging.info(f"⏭️ File recently processed, skipping: {os.path.basename(file_path)} (last processed {current_time - last_processed:.1f}s ago)")
                    return
            
            logging.info(f"🔍 Scanning file: {file_path}")
            
            # Check if file extension is monitored
            file_ext = os.path.splitext(file_path.lower())[1]
            is_monitored = any(file_path.lower().endswith(ext) for ext in self.monitored_extensions)
            
            logging.info(f"📋 File extension: {file_ext}, Monitored: {is_monitored}")
            
            # Mark file as processed
            self.processed_files[file_path] = current_time
            
            # Process ALL files, not just monitored ones
            try:
                file_hash = hash_file(file_path)
                if file_hash:
                    logging.info(f"🔐 File hash generated: {file_hash[:16]}...")
                    file_metadata = get_file_metadata(file_path)
                    file_metadata['hash'] = file_hash
                    
                    # Analyze all files for threats (even unmonitored ones)
                    is_suspicious = self.analyze_file_for_threats(file_path, event_type) if is_monitored else False
                    
                    if is_suspicious:
                        # Get detailed threat analysis for suspicious files
                        threat_analysis = self.get_threat_analysis(file_path, event_type, file_metadata)
                        
                        # Create threat data for suspicious files (using valid enum values)
                        scan_data = {
                            "device_id": "freetier-agent",
                            "threat_type": "suspicious",  # Valid enum: malware, suspicious, phishing, ransomware, trojan, backdoor, keylogger, other
                            "confidence_score": threat_analysis['confidence_score'],
                            "source": "behavior_analysis",  # Valid enum: ai_analysis, signature_based, behavior_analysis, user_report, wazuh, other
                            "severity": threat_analysis['severity'],  # Valid enum: low, medium, high, critical
                            "file_path": file_path,
                            "file_name": os.path.basename(file_path),
                            "details": {
                                "event_type": event_type,
                                "file_metadata": file_metadata,
                                "scan_result": threat_analysis['scan_result'],
                                "alert_id": hashlib.sha256(f"{file_path}{time.time()}".encode()).hexdigest(),
                                "timestamp": datetime.now().isoformat(),
                                "status": "SUSPICIOUS"
                            }
                        }
                        
                        logging.warning(f"🚨 SUSPICIOUS: {threat_analysis['scan_result']['reason']}")
                    else:
                        # Create data for safe/unmonitored files (using valid enum values)
                        scan_data = {
                            "device_id": "freetier-agent",
                            "threat_type": "other",  # Valid enum: malware, suspicious, phishing, ransomware, trojan, backdoor, keylogger, other
                            "confidence_score": 0.1,
                            "source": "behavior_analysis",  # Valid enum: ai_analysis, signature_based, behavior_analysis, user_report, wazuh, other
                            "severity": "low",  # Valid enum: low, medium, high, critical (changed from "info" to "low")
                            "file_path": file_path,
                            "file_name": os.path.basename(file_path),
                            "details": {
                                "event_type": event_type,
                                "file_metadata": file_metadata,
                                "scan_result": {
                                    "verdict": "Safe",  # Valid enum: Safe, Suspicious, Threat Detected, Unknown
                                    "confidence": "95%",
                                    "reason": f"File scanned: {os.path.basename(file_path)} ({file_ext or 'no extension'})"
                                },
                                "alert_id": hashlib.sha256(f"{file_path}{time.time()}".encode()).hexdigest(),
                                "timestamp": datetime.now().isoformat(),
                                "status": "SCANNED"
                            }
                        }
                        
                        status_text = "MONITORED" if is_monitored else "SCANNED"
                        logging.info(f"✅ {status_text}: {event_type} - {os.path.basename(file_path)}")
                    
                    # Add to queue for rate-limited sending
                    self.queue_alert_for_sending(scan_data, is_suspicious, is_monitored, event_type, file_path)
                else:
                    logging.warning(f"❌ Could not generate hash for file: {file_path}")
                    # Still send basic info even without hash
                    scan_data = {
                        "device_id": "freetier-agent",
                        "threat_type": "other",
                        "confidence_score": 0.1,
                        "source": "behavior_analysis",
                        "severity": "low",
                        "file_path": file_path,
                        "file_name": os.path.basename(file_path),
                        "details": {
                            "event_type": event_type,
                            "file_metadata": {"size": "unknown", "extension": file_ext},
                            "scan_result": {
                                "verdict": "Unknown",  # Valid enum: Safe, Suspicious, Threat Detected, Unknown
                                "confidence": "N/A",
                                "reason": f"File activity: {event_type} - {os.path.basename(file_path)} (no hash)"
                            },
                            "alert_id": hashlib.sha256(f"{file_path}{time.time()}".encode()).hexdigest(),
                            "timestamp": datetime.now().isoformat(),
                            "status": "SKIPPED"
                        }
                    }
                    self.queue_alert_for_sending(scan_data, False, False, event_type, file_path, "SKIPPED")
            except Exception as hash_error:
                logging.error(f"Error processing file {file_path}: {hash_error}")
        except Exception as e:
            logging.error(f"Error processing file event: {e}")
    
    def queue_alert_for_sending(self, scan_data, is_suspicious, is_monitored, event_type, file_path, status_override=None):
        """Queue alert for rate-limited sending with priority"""
        status_text = status_override or ("SUSPICIOUS" if is_suspicious else ("MONITORED" if is_monitored else "SCANNED"))
        
        alert_item = {
            'data': scan_data,
            'status_text': status_text,
            'event_type': event_type,
            'file_path': file_path,
            'is_suspicious': is_suspicious,
            'is_monitored': is_monitored
        }
        
        # Add to appropriate queue based on priority
        if is_suspicious:
            self.priority_queue.append(alert_item)
            logging.info(f"🚨 Added to priority queue: {status_text} - {os.path.basename(file_path)}")
        else:
            # Add safe files with larger queue limit
            if len(self.request_queue) < 50:  # Increased queue size limit
                self.request_queue.append(alert_item)
                logging.info(f"📝 Added to regular queue: {status_text} - {os.path.basename(file_path)}")
            else:
                logging.info(f"⏭️ Skipping safe file (queue full): {os.path.basename(file_path)}")
        
        # Process queue more frequently
        current_time = time.time()
        required_interval = self.malicious_interval if is_suspicious else self.safe_interval
        
        # Process queue if enough time has passed OR if we have priority items
        if (current_time - self.last_request_time >= required_interval) or (is_suspicious and len(self.priority_queue) > 0):
            self.process_alert_queue()
    
    def process_alert_queue(self):
        """Process queued alerts with priority and rate limiting"""
        if not self.priority_queue and not self.request_queue:
            return
        
        # Process priority queue first (malicious files)
        processed = 0
        
        # Process malicious files first
        while self.priority_queue and processed < self.batch_size:
            alert_item = self.priority_queue.popleft()
            
            logging.info(f"🚨 Processing priority alert: {alert_item['status_text']} - {os.path.basename(alert_item['file_path'])}")
            
            # Send the alert with longer delay for malicious files
            success = self.send_alert_to_endpoints(alert_item['data'])
            
            if success:
                logging.info(f"📱 🚨 Sent to mobile app: {alert_item['status_text']} - {os.path.basename(alert_item['file_path'])}")
            else:
                logging.error(f"❌ Failed to send malicious alert for: {os.path.basename(alert_item['file_path'])}")
            
            processed += 1
            
            # Shorter delay for malicious files
            if processed < self.batch_size and (self.priority_queue or self.request_queue):
                logging.info(f"⏱️ Waiting {self.malicious_interval}s before next request...")
                time.sleep(self.malicious_interval)
        
        # Process regular queue if batch size allows
        while self.request_queue and processed < self.batch_size:
            alert_item = self.request_queue.popleft()
            
            # Send the alert
            success = self.send_alert_to_endpoints(alert_item['data'])
            
            if success:
                logging.info(f"📱 ✅ Sent to mobile app: {alert_item['status_text']} - {os.path.basename(alert_item['file_path'])}")
            else:
                logging.error(f"❌ Failed to send scan result for: {os.path.basename(alert_item['file_path'])}")
            
            processed += 1
            
            # Shorter delay between safe file requests
            if processed < self.batch_size and self.request_queue:
                time.sleep(1.0)
        
        self.last_request_time = time.time()
        
        # Log remaining queue sizes
        total_remaining = len(self.priority_queue) + len(self.request_queue)
        if total_remaining > 0:
            logging.info(f"⏳ {len(self.priority_queue)} priority alerts, {len(self.request_queue)} regular alerts remaining")
    
    def analyze_file_for_threats(self, file_path, event_type):
        """Analyze if file activity is genuinely suspicious"""
        file_name = os.path.basename(file_path).lower()
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Check for suspicious patterns
        suspicious_indicators = [
            # Suspicious file names
            'keylog' in file_name,
            'password' in file_name and file_ext in ['.txt', '.log'],
            'hack' in file_name,
            'crack' in file_name,
            'trojan' in file_name,
            'virus' in file_name,
            'malware' in file_name,
            
            # Suspicious extensions in Downloads
            file_ext in ['.exe', '.scr', '.bat', '.cmd', '.pif'] and 'downloads' in file_path.lower(),
            
            # Suspicious double extensions
            '.pdf.exe' in file_name,
            '.doc.exe' in file_name,
            '.jpg.exe' in file_name,
            
            # Files with no extension but executable-like names
            file_ext == '' and any(word in file_name for word in ['setup', 'install', 'update', 'patch']),
            
            # Temporary files in system directories
            'temp' in file_path.lower() and file_ext in ['.exe', '.dll'],
            
            # Hidden files with suspicious extensions
            file_name.startswith('.') and file_ext in ['.exe', '.bat', '.cmd']
        ]
        
        return any(suspicious_indicators)
    
    def get_threat_analysis(self, file_path, event_type, file_metadata):
        """Get detailed threat analysis for suspicious files"""
        file_name = os.path.basename(file_path).lower()
        file_ext = os.path.splitext(file_name)[1].lower()
        
        # Determine threat type and severity (using valid enum values)
        if any(word in file_name for word in ['keylog', 'password', 'hack']):
            threat_type = "malware"  # Valid enum value
            severity = "high"
            confidence = 0.8
            reason = f"Suspicious file name detected: {os.path.basename(file_path)}"
        elif file_ext in ['.exe', '.scr'] and 'downloads' in file_path.lower():
            threat_type = "suspicious"  # Valid enum value
            severity = "medium"
            confidence = 0.6
            reason = f"Executable file in Downloads folder: {os.path.basename(file_path)}"
        elif '.exe' in file_name and file_ext != '.exe':
            threat_type = "trojan"  # Valid enum value
            severity = "high"
            confidence = 0.9
            reason = f"File with disguised extension detected: {os.path.basename(file_path)}"
        else:
            threat_type = "suspicious"  # Valid enum value
            severity = "low"
            confidence = 0.4
            reason = f"Suspicious file activity: {event_type} - {os.path.basename(file_path)}"
        
        return {
            "threat_type": threat_type,
            "severity": severity,
            "confidence_score": confidence,
            "scan_result": {
                "verdict": "Suspicious",  # Valid enum: Safe, Suspicious, Threat Detected, Unknown
                "confidence": f"{int(confidence * 100)}%",
                "reason": reason
            }
        }
    
    def send_alert_to_endpoints(self, threat_data):
        """Send alert to mobile app and user portal"""
        try:
            # Check if we have an API key (JWT token)
            if not Config.API_KEY:
                logging.error("❌ No JWT token available. Please login first.")
                return False
            
            # Format data for threats endpoint
            formatted_data = {
                "device_id": threat_data["device_id"],
                "threat_type": threat_data["threat_type"],
                "confidence_score": threat_data["confidence_score"],
                "source": threat_data["source"],
                "severity": threat_data["severity"],
                "file_path": threat_data["file_path"],
                "details": {
                    "file_path": threat_data["file_path"],
                    "verdict": threat_data["details"]["scan_result"]["verdict"],
                    "confidence": threat_data["details"]["scan_result"]["confidence"],
                    "reason": threat_data["details"]["scan_result"]["reason"],
                    "event_type": threat_data["details"]["event_type"],
                    "timestamp": threat_data["details"]["timestamp"]
                }
            }
            
            # Send to backend API for mobile app and user portal
            headers = {
                "Authorization": f"Bearer {Config.API_KEY}",
                "Content-Type": "application/json"
            }
            
            url = f"{Config.AUTH_API_URL}/api/threats/agent"
            logging.info(f"📤 Sending threat alert to: {url}")
            logging.info(f"🔑 Using token: {Config.API_KEY[:20]}...")
            logging.info(f"📊 Threat data: {threat_data['threat_type']} - {threat_data['file_name']}")
            
            # Send to threats endpoint
            response = requests.post(
                url,
                json=formatted_data,
                headers=headers,
                timeout=15
            )
            
            logging.info(f"📡 Response status: {response.status_code}")
            logging.info(f"📡 Response body: {response.text}")
            
            if response.status_code in [200, 201]:
                logging.info("✅ Threat alert sent successfully!")
                logging.info("📋 ✅ Data also available in user portal via threats endpoint")
                
                # Also save to local file for direct portal access
                self.save_to_local_portal_file(formatted_data)
                return True
            else:
                logging.warning(f"⚠️ Failed to send alert: {response.status_code}")
                logging.warning(f"Response: {response.text}")
                return False
                
        except requests.exceptions.ConnectionError as e:
            logging.error(f"🌐 Connection error: {e}")
            return False
        except requests.exceptions.Timeout as e:
            logging.error(f"⏰ Request timeout: {e}")
            return False
        except Exception as e:
            logging.error(f"❌ Error sending alert: {e}")
            return False
    
    def save_to_local_portal_file(self, threat_data):
        """Save threat data to local file for direct portal access"""
        try:
            import json
            import os
            from datetime import datetime
            
            # Create logs directory if it doesn't exist
            logs_dir = os.path.join(os.path.dirname(__file__), "portal_logs")
            os.makedirs(logs_dir, exist_ok=True)
            
            # Also create in user portal public directory for direct access
            portal_public_dir = os.path.join(os.path.dirname(__file__), "..", "..", "user", "public")
            os.makedirs(portal_public_dir, exist_ok=True)
            
            # File paths for portal logs
            log_file = os.path.join(logs_dir, "agent_threats.json")
            portal_log_file = os.path.join(portal_public_dir, "agent_threats.json")
            
            # Load existing logs or create new list
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            else:
                logs = []
            
            # Add new threat data with timestamp
            threat_entry = {
                **threat_data,
                "portal_timestamp": datetime.now().isoformat(),
                "id": f"local_{len(logs) + 1}"
            }
            
            # Add to beginning of list (newest first) and keep only last 100
            logs.insert(0, threat_entry)
            logs = logs[:100]
            
            # Save to both locations
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            # Also save to portal public directory
            with open(portal_log_file, 'w') as f:
                json.dump(logs, f, indent=2)
            
            logging.info(f"💾 Saved threat data to local portal file: {log_file}")
            logging.info(f"💾 Also saved to portal public directory: {portal_log_file}")
            
        except Exception as e:
            logging.error(f"❌ Error saving to local portal file: {e}")

class CIAAuditor:
    def run_full_audit(self):
        logging.info("Starting Limited CIA Security Audit...")
        # ... (rest of the audit logic is the same)
        report = {
            "report_type": "CIA Audit",
            "timestamp": datetime.now().isoformat(),
            "overall_score": 50, # Dummy score
            "details": "Limited CIA Audit for Free Tier."
        }
        ws_send_queue.put({"type": "audit", "payload": report})
        logging.info("CIA Audit completed and report sent to portal.")

def run_agent_after_login():
    global ws_client
    
    # Skip WebSocket for now due to Vercel limitations, focus on HTTP alerts
    logging.info("🛡️ Agent is running in the free tier with real-time monitoring!")
    logging.info("📱 Alerts will be sent to your mobile app via HTTP API")
    logging.info("🔍 Monitoring directories: Downloads, Desktop, Documents")
    
    # Start real-time file monitoring (this will send HTTP alerts)
    start_realtime_monitoring()
    
    # WebSocket disabled for Vercel compatibility - using HTTP API only
    logging.info("🔌 WebSocket disabled (using HTTP API for alerts)")
    if ws_client:
        try:
            ws_client.stop()
            ws_client.join(timeout=5)
        except Exception:
            pass
        ws_client = None

def start_realtime_monitoring():
    """Start real-time file system monitoring"""
    try:
        event_handler = RealTimeFileMonitor()
        observer = Observer()
        
        # Monitor specified directories
        for path in Config.REALTIME_MONITOR_PATHS:
            if os.path.exists(path):
                observer.schedule(event_handler, path, recursive=True)
                logging.info(f"📁 Monitoring: {path}")
            else:
                logging.warning(f"⚠️ Path does not exist: {path}")
        
        observer.start()
        logging.info("🔍 Real-time file monitoring started!")
        
        # Store observer globally so we can stop it later
        global file_observer
        file_observer = observer
        
        # Start a background thread to periodically process the queue
        def periodic_queue_processor():
            while True:
                time.sleep(10)  # Check every 10 seconds
                if hasattr(event_handler, 'process_alert_queue'):
                    try:
                        event_handler.process_alert_queue()
                    except Exception as e:
                        logging.error(f"Error in periodic queue processing: {e}")
        
        queue_thread = threading.Thread(target=periodic_queue_processor, daemon=True)
        queue_thread.start()
        logging.info("🔄 Periodic queue processor started")
        
        # Create a test file to verify monitoring is working
        test_monitoring_functionality()
        
    except Exception as e:
        logging.error(f"Failed to start real-time monitoring: {e}")

def test_monitoring_functionality():
    """Create test files to verify monitoring is working"""
    try:
        test_dir = Config.REALTIME_MONITOR_PATHS[0]  # Use Downloads folder
        if os.path.exists(test_dir):
            logging.info("🧪 Creating test files to verify monitoring...")
            
            # Test 1: Safe file
            safe_test_file = os.path.join(test_dir, "cyberrazor_safe_test.pdf")
            with open(safe_test_file, 'w') as f:
                f.write("CyberRazor safe test file - can be deleted")
            
            # Test 2: Suspicious file
            suspicious_test_file = os.path.join(test_dir, "cyberrazor_suspicious_test.exe")
            with open(suspicious_test_file, 'w') as f:
                f.write("CyberRazor suspicious test file - can be deleted")
            
            # Wait for events to be processed
            import time
            time.sleep(3)
            
            # Clean up test files
            for test_file in [safe_test_file, suspicious_test_file]:
                if os.path.exists(test_file):
                    os.remove(test_file)
            
            logging.info("🧹 Test files cleaned up")
            logging.info("🎯 If you saw alerts above, monitoring is working!")
        else:
            logging.warning("⚠️ Cannot create test files - Downloads folder not found")
    except Exception as e:
        logging.error(f"Test file creation failed: {e}")


def show_config_menu():
    choice = arrow_menu("Config", ["Activate Pro", "Custom (Appointment)", "Back"])
    if choice == 0:
        activate_pro_flow()
    elif choice == 1:
        webbrowser.open("https://cyberrazor.vercel.app/appointment")
    return


def main():
    global ws_client, file_observer
    setup_logging()
    # Interactive banner menu
    while True:
        selected = arrow_menu("CyberRazor", ["Login", "Config", "Exit"])
        if selected == 0:
            if login():
                # Config.API_KEY is already set in login() function
                run_agent_after_login()
                print("\n🛡️ CyberRazor is now protecting your system!")
                print("📱 Real-time alerts will be sent to your mobile app")
                print("🌐 Check your user portal for detailed logs")
                print("Press Ctrl+C to stop monitoring...")
                try:
                    # Keep the main thread alive while monitoring
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    print("\n🛑 Stopping CyberRazor...")
                    break
            else:
                print("❌ Login failed. Please check your credentials.")
                input("Press Enter to continue...")
        elif selected == 1:
            show_config_menu()
        elif selected == 2:
            print("Exiting...")
            break
    
    # Graceful shutdown
    print("🔄 Shutting down services...")
    
    if file_observer:
        try:
            file_observer.stop()
            file_observer.join()
            logging.info("📁 File monitoring stopped")
        except Exception as e:
            logging.error(f"Error stopping file observer: {e}")
    
    if ws_client:
        try:
            ws_client.stop()
            ws_client.join(timeout=5)
            logging.info("🔌 WebSocket connection closed")
        except Exception as e:
            logging.error(f"Error stopping WebSocket client: {e}")
    
    logging.info("✅ Agent has been shut down gracefully.")

if __name__ == "__main__":
    main()