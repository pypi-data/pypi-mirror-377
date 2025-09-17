import requests
import platform
from urllib.parse import urlencode


class NetworkHandler:
    def __init__(self, base_url, api_base_path, handler_version, instance_marker):
        self.base_url = base_url
        self.api_base_path = api_base_path
        self.handler_version = handler_version
        self.instance_marker = instance_marker
        self.http_client = requests.Session()
        self.http_client.headers.update({
            'User-Agent': f'UpdateClient/{handler_version} ({platform.system()}; {instance_marker})'
        })
        self.api_action_segments = {
            'sync_check': 'check_update',
            'fetch_directive': 'get_directive',
            'report_outcome': 'report_directive_result',
            'update_directive_status': 'update_queued_directive_status',
            'asset_download': 'asset_retrieval',
            'error_report': 'report_client_error'
        }
    
    def construct_endpoint(self, action_key):
        segment = self.api_action_segments.get(action_key)
        if not segment:
            return None
        return f"{self.base_url}{self.api_base_path}{segment}"
    
    def send_request(self, action_key, payload, signature, is_json=True, timeout=30):
        url = self.construct_endpoint(action_key)
        if not url:
            print(f"Invalid action key: {action_key}")
            return None
        
        headers = {
            'X-Signature': signature
        }
        
        if is_json:
            headers['Content-Type'] = 'application/json'
            if isinstance(payload, str):
                data = payload
            else:
                import json
                data = json.dumps(payload)
        else:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            if isinstance(payload, dict):
                data = urlencode(payload)
            else:
                data = payload
        
        try:
            response = self.http_client.post(
                url,
                data=data,
                headers=headers,
                timeout=timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"HTTP Error {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
    
    def download_asset(self, payload, signature):
        url = self.construct_endpoint('asset_download')
        if not url:
            return None
        
        headers = {
            'X-Signature': signature,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        try:
            response = self.http_client.post(
                url,
                data=urlencode(payload),
                headers=headers,
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Asset download failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Asset download failed: {e}")
            return None
    
    def report_error(self, error_data, signature):
        url = self.construct_endpoint('error_report')
        if not url:
            return False
        
        try:
            import json
            response = self.http_client.post(
                url,
                data=json.dumps(error_data),
                headers={
                    'Content-Type': 'application/json',
                    'X-Signature': signature
                },
                timeout=15
            )
            
            return 200 <= response.status_code < 300
            
        except Exception as e:
            print(f"Error reporting failed: {e}")
            return False