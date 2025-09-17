import requests
import json
from typing import Dict, Any, Optional, List
from .types import UserContext, ClientConfig, RequestOptions, ApiResponse, PaginatedResponse

class BaseClient:
    def __init__(self, config: ClientConfig, service_name: str):
        self.config = config
        self.service_name = service_name  # 存储为实例变量
        self.user_context = None
        self.token = None
        
        # 确定基础URL
        self.base_url = self._get_base_url()
        
        # 创建session
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def _get_base_url(self):
        # 使用 self.service_name 而不是直接访问 service_name
        service_urls = {
            'auth': self.config.auth_service_url,
            'msg': self.config.msg_service_url,
            'users': self.config.user_service_url,
            'file': self.config.file_service_url,
            'survey': self.config.survey_service_url,
            'token': self.config.token_service_url,
        }
        
        # 检查服务名称是否在支持的列表中
        if self.service_name not in service_urls:
            raise ValueError(f"Unsupported service: {self.service_name}")
        
        return service_urls[self.service_name]
    
    def set_user_context(self, context: UserContext):
        self.user_context = context
        return self
    
    def set_token(self, token: str):
        self.token = token
        return self
    
    def _init_user_context_headers(self, context: UserContext) -> Dict[str, str]:
        return {
            'v-user-id': context.user_id,
            'v-user-role': context.role,
            'v-project-id': context.project_id
        }
    
    def _handle_api_error(self, error, path):
        error_message = f"[{self.service_name}服务] "
        
        if hasattr(error, 'response') and error.response is not None:
            response = error.response
            try:
                response_data = response.json()
                if 'message' in response_data:
                    error_message += response_data['message']
                elif 'error' in response_data:
                    error_message += response_data['error']
                else:
                    error_message += f"请求失败，状态码: {response.status_code}"
            except:
                error_message += f"请求失败，状态码: {response.status_code}"
            
            # 添加详细错误信息
            error_message += f" | 状态码: {response.status_code}"
            if 'x-request-id' in response.headers:
                error_message += f" | 请求ID: {response.headers['x-request-id']}"
        else:
            error_message += str(error)
        
        # 添加路径信息
        error_message += f" (路径: {path})"
        
        raise Exception(error_message)
    
    def request(self, path: str, options: RequestOptions = None) -> Any:
        if options is None:
            options = RequestOptions(method='GET')
        
        try:
            url = f"{self.base_url}{path}"
            
            # 准备请求参数
            headers = options.headers.copy() if options.headers else {}
            
            # 添加用户上下文
            context = options.user_context or self.user_context
            if context:
                headers.update(self._init_user_context_headers(context))
            
            # 添加认证令牌
            if self.token:
                headers['Authorization'] = f"Bearer {self.token}"
            
            # 发送请求
            response = self.session.request(
                method=options.method,
                url=url,
                headers=headers,
                params=options.params,
                json=options.body,
                timeout=30
            )
            
            # 检查HTTP状态
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 检查业务成功状态
            if not response_data.get('success', False):
                raise Exception(response_data.get('message', '业务请求失败'))
            
            # 返回实际数据
            return response_data.get('data')
            
        except Exception as error:
            self._handle_api_error(error, path)
    
    def paginated_request(self, path: str, options: RequestOptions = None) -> PaginatedResponse:
        if options is None:
            options = RequestOptions(method='GET')
        
        try:
            url = f"{self.base_url}{path}"
            
            # 准备请求参数
            headers = options.headers.copy() if options.headers else {}
            
            # 添加用户上下文
            context = options.user_context or self.user_context
            if context:
                headers.update(self._init_user_context_headers(context))
            
            # 添加认证令牌
            if self.token:
                headers['Authorization'] = f"Bearer {self.token}"
            
            # 发送请求
            response = self.session.request(
                method=options.method,
                url=url,
                headers=headers,
                params=options.params,
                json=options.body,
                timeout=30
            )
            
            # 检查HTTP状态
            response.raise_for_status()
            
            # 解析响应
            response_data = response.json()
            
            # 检查业务成功状态
            if not response_data.get('success', False):
                raise Exception(response_data.get('message', '业务请求失败'))
            
            # 返回分页响应
            return PaginatedResponse(
                data=response_data.get('data', []),
                success=response_data.get('success', False),
                message=response_data.get('message', ''),
                pagination=response_data.get('pagination', {})
            )
            
        except Exception as error:
            self._handle_api_error(error, path)