from .base_client import BaseClient
from .types import RequestOptions, MailRequest, FeishuMessage

class MsgService(BaseClient):
    def __init__(self, config):
        super().__init__(config, 'msg')
    
    def send_mail(self, request: MailRequest, options: RequestOptions = None):
        return self.request('/mail/send', RequestOptions(
            method='POST',
            body=request,
            headers=options.headers if options else None
        ))
    
    def send_feishu_message(self, message: FeishuMessage, options: RequestOptions = None):
        return self.request('/webhook/feishu/send', RequestOptions(
            method='POST',
            body=message,
            headers=options.headers if options else None
        ))