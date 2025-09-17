from .base_client import BaseClient
from .types import RequestOptions, LoginResponse

class AuthService(BaseClient):
    def __init__(self, config):
        super().__init__(config, 'auth')
    
    def login(self, identifier: str, password: str, project_id: int = 0, options: RequestOptions = None) -> LoginResponse:
        body = {
            'grant_type': 'password',
            'username': identifier,
            'password': password
        }
        
        headers = {}
        if options and options.headers:
            headers = options.headers.copy()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
        
        return self.request('/login', RequestOptions(
            method='POST',
            headers=headers,
            params={'project_id': project_id},
            body=body
        ))
    
    def logout(self, token: str, options: RequestOptions = None):
        headers = {}
        if options and options.headers:
            headers = options.headers.copy()
        headers['Authorization'] = f'Bearer {token}'
        
        return self.request('/logout', RequestOptions(
            method='POST',
            headers=headers
        ))