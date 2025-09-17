from .base_client import BaseClient
from .types import RequestOptions, PaginatedResponse, User, UserCreateRequest, UserUpdateRequest

class UserService(BaseClient):
    def __init__(self, config):
        super().__init__(config, 'users')
    
    def get_current_user(self, options: RequestOptions = None) -> User:
        return self.request('/me', RequestOptions(
            method='GET',
            headers=options.headers if options else None
        ))
    
    def create_user(self, user_data: UserCreateRequest, options: RequestOptions = None) -> User:
        return self.request('', RequestOptions(
            method='POST',
            body={
                'username': user_data.username,
                'email': user_data.email,
                'password': user_data.password,
                'name': user_data.name,
                'role': user_data.role,
                'phone': user_data.phone,
                'project_id': user_data.project_id
            },
            headers=options.headers if options else None
        ))
    
    def update_user(self, user_id: int, update_data: UserUpdateRequest, options: RequestOptions = None) -> User:
        return self.request(f'/{user_id}', RequestOptions(
            method='PUT',
            body={
                'name': update_data.name,
                'avatar': update_data.avatar,
                'phone': update_data.phone,
                'role': update_data.role,
                'project_id': update_data.project_id
            },
            headers=options.headers if options else None
        ))
    
    def list_users(self, include_inactive: bool = False, page: int = 1, per_page: int = 10, options: RequestOptions = None) -> PaginatedResponse[User]:
        return self.paginated_request('', RequestOptions(
            method='GET',
            params={
                'include_inactive': include_inactive,
                'page': page,
                'per_page': per_page
            },
            headers=options.headers if options else None
        ))