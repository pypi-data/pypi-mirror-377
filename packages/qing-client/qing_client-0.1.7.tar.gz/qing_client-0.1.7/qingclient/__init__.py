from .auth_service import AuthService
from .msg_service import MsgService
from .token_service import TokenService
from .user_service import UserService
from .base_client import BaseClient
from .types import ClientConfig, UserContext
from .types import *


class QingClient:
    def __init__(self, config:ClientConfig):
        self.config = config
        self.auth = AuthService(config)
        self.msg = MsgService(config)
        self.token = TokenService(config)
        self.user = UserService(config)
    
    def set_user_context(self, context):
        self.auth.set_user_context(context)
        self.msg.set_user_context(context)
        self.token.set_user_context(context)
        self.user.set_user_context(context)
        return self