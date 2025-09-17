import sys
import subprocess
import json
import requests
from packaging import version
from .utils import log_to_file

try:
    from importlib.metadata import version as get_package_version
except ImportError:
    from importlib_metadata import version as get_package_version

class SelfUpdater:

    def __init__(self):
        self.package_name = "spamir-updater"
        self.pypi_url = f"https://pypi.org/pypi/{self.package_name}/json"
        self.current_version = self._get_current_version()

    def _get_current_version(self):
        try:
            return get_package_version(self.package_name)
        except Exception as e:
            log_to_file(f"Package {self.package_name} not found in installed packages: {e}", 'WARNING')
            return "0.0.0"

    def _get_latest_version_from_pypi(self):
        try:
            response = requests.get(self.pypi_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data['info']['version']
        except requests.exceptions.RequestException as e:
            log_to_file(f"Failed to fetch version info from PyPI: {e}", 'ERROR')
            return None
        except (KeyError, json.JSONDecodeError) as e:
            log_to_file(f"Failed to parse PyPI response: {e}", 'ERROR')
            return None

    def check_for_update(self):
        latest_version = self._get_latest_version_from_pypi()

        if not latest_version:
            return {
                'update_available': False,
                'current_version': self.current_version,
                'latest_version': None,
                'error': 'Failed to check for updates'
            }

        try:
            current_ver = version.parse(self.current_version)
            latest_ver = version.parse(latest_version)

            update_available = latest_ver > current_ver

            return {
                'update_available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'error': None
            }
        except Exception as e:
            log_to_file(f"Version comparison failed: {e}", 'ERROR')
            return {
                'update_available': False,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'error': f'Version comparison failed: {e}'
            }

    def perform_self_update(self, force=False):
        if not force:
            update_info = self.check_for_update()
            if update_info.get('error'):
                return {
                    'success': False,
                    'message': f"Update check failed: {update_info['error']}",
                    'current_version': self.current_version,
                    'target_version': None
                }

            if not update_info['update_available']:
                return {
                    'success': True,
                    'message': 'Already running the latest version',
                    'current_version': self.current_version,
                    'target_version': update_info['latest_version']
                }

            target_version = update_info['latest_version']
        else:
            target_version = self._get_latest_version_from_pypi()
            if not target_version:
                return {
                    'success': False,
                    'message': 'Failed to get target version for forced update',
                    'current_version': self.current_version,
                    'target_version': None
                }

        try:
            log_to_file(f"Starting self-update from {self.current_version} to {target_version}", 'INFO')

            cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', self.package_name]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode == 0:
                log_to_file(f"Self-update completed successfully to version {target_version}", 'INFO')
                return {
                    'success': True,
                    'message': f'Successfully updated from {self.current_version} to {target_version}',
                    'current_version': self.current_version,
                    'target_version': target_version,
                    'restart_required': True
                }
            else:
                error_msg = result.stderr or result.stdout or 'Unknown error'
                log_to_file(f"Self-update failed: {error_msg}", 'ERROR')
                return {
                    'success': False,
                    'message': f'Update failed: {error_msg}',
                    'current_version': self.current_version,
                    'target_version': target_version
                }

        except subprocess.TimeoutExpired:
            log_to_file("Self-update timed out", 'ERROR')
            return {
                'success': False,
                'message': 'Update timed out',
                'current_version': self.current_version,
                'target_version': target_version
            }
        except Exception as e:
            log_to_file(f"Self-update error: {e}", 'ERROR')
            return {
                'success': False,
                'message': f'Update error: {e}',
                'current_version': self.current_version,
                'target_version': target_version
            }

    def get_version_info(self):
        update_info = self.check_for_update()

        return {
            'package_name': self.package_name,
            'current_version': self.current_version,
            'latest_version': update_info.get('latest_version'),
            'update_available': update_info.get('update_available', False),
            'error': update_info.get('error')
        }