import json
import os
import platform
import sys
import hashlib
import uuid
import socket
import datetime
import tempfile
import subprocess
import shutil
import time
from pathlib import Path


def load_version_from_config():
    config_path = Path.cwd() / 'config.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return str(config.get('version')) if config.get('version') else None
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return None


def save_version_to_config(version):
    config_path = Path.cwd() / 'config.json'
    config = {}
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    config['version'] = version
    
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save version to config: {e}")
        return False


def get_system_info():
    profile = {
        'diag_version': '1.2',
        'os_platform': sys.platform,
        'python_version': sys.version,
        'os_architecture': platform.machine(),
        'runtime_ver': f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    }
    
    try:
        profile['os_release'] = platform.release()
    except Exception:
        profile['os_release'] = 'unknown'
    
    return profile


def get_system_component():
    try:
        import psutil

        interfaces = []
        for interface_name, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family == psutil.AF_LINK:
                    mac = addr.address
                    if mac and mac != '00:00:00:00:00:00':
                        is_low_priority = (
                            interface_name.lower().startswith('lo') or
                            interface_name.lower().startswith('vmnet') or
                            interface_name.lower().startswith('docker')
                        )

                        interfaces.append({
                            'name': interface_name,
                            'mac': mac.replace(':', '').upper(),
                            'priority': 1 if is_low_priority else 0
                        })

        if not interfaces:
            return os.urandom(16).hex().upper()

        def sort_key(interface):
            priority = interface['priority']
            name = interface['name'].lower()

            preferred_prefixes = ['eth', 'en', 'wlan']
            prefix_index = -1

            for i, prefix in enumerate(preferred_prefixes):
                if name.startswith(prefix):
                    prefix_index = i
                    break

            return (priority, prefix_index if prefix_index != -1 else 999, name)

        interfaces.sort(key=sort_key)
        return interfaces[0]['mac']

    except ImportError:
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff)
                          for elements in range(0, 8*6, 8)][::-1])
            if mac != '00:00:00:00:00:00':
                return mac.replace(':', '').upper()
        except Exception:
            pass

        return os.urandom(16).hex().upper()

    except Exception:
        return os.urandom(16).hex().upper()


def generate_instance_signature(auth_token):
    system_component = get_system_component()
    id_material = system_component + auth_token
    OID_NAMESPACE = uuid.UUID('6ba7b812-9dad-11d1-80b4-00c04fd430c8')
    return str(uuid.uuid5(OID_NAMESPACE, id_material))


def log_to_file(message, level='INFO'):
    timestamp = datetime.datetime.now().isoformat()
    print(f"[{timestamp}] [{level}] {message}")


def create_temp_workspace(prefix=None):
    workspace = tempfile.mkdtemp(prefix=prefix or '')
    os.chmod(workspace, 0o700)
    return workspace


def secure_delete(file_path):
    try:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            if size > 0:
                with open(file_path, 'rb+') as f:
                    f.write(os.urandom(size))
                    f.flush()
                    os.fsync(f.fileno())
            os.remove(file_path)
            return True
    except Exception:
        try:
            os.remove(file_path)
        except Exception:
            pass
        return False


def sanitize_workspace(workspace_path):
    try:
        if os.path.exists(workspace_path):
            for root, dirs, files in os.walk(workspace_path):
                for file in files:
                    secure_delete(os.path.join(root, file))
            shutil.rmtree(workspace_path, ignore_errors=True)
        return True
    except Exception:
        return False


def cleanup_workspace(workspace_path):
    return sanitize_workspace(workspace_path)


def run_isolated_process(script_path, timeout=300, workspace=None):
    stdout_file = os.path.join(workspace or os.path.dirname(script_path), 'o')
    stderr_file = os.path.join(workspace or os.path.dirname(script_path), 'e')

    with open(stdout_file, 'w') as stdout_f, open(stderr_file, 'w') as stderr_f:
        if os.name == 'nt':
            creation_flags = subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS
            preexec_fn = None
            start_new_session = False
        else:
            creation_flags = 0
            preexec_fn = None
            start_new_session = True

        process = subprocess.Popen(
            [sys.executable, script_path],
            stdout=stdout_f,
            stderr=stderr_f,
            stdin=subprocess.DEVNULL,
            cwd=workspace or os.path.dirname(script_path),
            creationflags=creation_flags,
            preexec_fn=preexec_fn,
            start_new_session=start_new_session
        )

    return process, stdout_file, stderr_file


def read_process_output(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception:
        pass
    return ""