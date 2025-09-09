'''
    vsrv - Base Handlers
'''
from http import HTTPStatus
from typing import Any
import bson
import tornado
import tornado.web
from vsrv.net.body import HTTPBody
from vsrv.models import const_models, config_models, config_keys
from vsrv.logging.insight import SystemInsight


class BaseRequestHandler(tornado.web.RequestHandler):
    '''
        vsrv - Base Request Handler
    '''

    def __init__(self, application, request, **kwargs: Any) -> None:
        '''
            Constructor
        '''
        super().__init__(application, request, **kwargs)
        self.LogLevelName: str = "Base"
        self.AppConstantSetting: const_models.SystemConstantModel
        self.AppConfigurationSetting: config_models.ConfigurationModel
        self.ChannelAuthenticationId: str = ''
        self.ChannelAuthenticationKey: str = ''

    def initialize(self):
        '''
            Initialize Class Parameters
        '''
        self.LogLevelName: str = 'Base'
        self.AppConstantSetting: const_models.SystemConstantModel = self.application.settings[config_keys.APP_CONSTANT_KEY]
        self.AppConfigurationSetting: config_models.ConfigurationModel = self.application.settings[config_keys.APP_CONFIGURATION_KEY]

    def prepare(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.add_header("Access-Control-Allow-Origin", "*")
        self.add_header("Content-Type", "application/json")
        # self.add_header("V-Application", self.AppConstantSetting.Application.Title)
        # self.add_header("V-Application-Version", self.AppConstantSetting.Application.Version)
        # self.add_header("V-Application-Environment", self.AppConstantSetting.Application.Environment)

    def check_auth_headers(self) -> bool:
        '''
            Validate's Request Authentication Headers
        '''
        if not config_keys.APP_REQUEST_HEADER_AUTH_ID_KEY in self.request.headers.keys() or not config_keys.APP_REQUEST_HEADER_AUTH_KEY_KEY in self.request.headers.keys():
            # ! Authentication Headers Missing
            log_msg = f'{self.request.method}::{self.request.full_url()} : AUTHENTICATION HEADERS MISSING'
            SystemInsight.logger().warning(log_msg)
            self.not_ok(
                msg="Authentication Headers Missing. Expecting V-AUTH-ID & V-AUTH-KEY in Request Headers",
                http_status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
            return False

        # * Authentication Headers Found
        self.ChannelAuthenticationId = self.request.headers[config_keys.APP_REQUEST_HEADER_AUTH_ID_KEY]
        self.ChannelAuthenticationKey = self.request.headers[config_keys.APP_REQUEST_HEADER_AUTH_KEY_KEY]

        # ? Checking AuthenticationID Type
        try:
            bson.ObjectId(self.ChannelAuthenticationId)
            # * Authentication Id : Valid
            return True
        except Exception as excp:
            # ! Authentication Id : Invalid
            log_msg = f'{self.request.method}::{self.request.full_url()} : INVALID AUTHENTICATION ID FORMAT'
            SystemInsight.logger().warning(log_msg)
            self.not_ok(
                msg="Invalid Value for Authentication Header's V-AUTH-ID",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=excp
            )
            return False

    def full_request_url(self):
        '''
            Provides Application Full Request URL
        '''
        return f"{self.request.protocol}//{self.request.host}/{self.request.uri}"

    def base_url(self):
        '''
            Provides Application base URL
        '''
        return f'{self.request.protocol}://{self.request.host}'

    def payment_callball_url(self):
        '''
            Provides Payment Call URL in System
        '''
        return f'{self.base_url()}/paymentCallback'

    def request_to_dict(self):
        '''
            Represent Request Content as Dictionary
        '''
        req_data = {
            'abs_uri': f'{self.request.protocol}://{self.request.host}{self.request.uri}',
            'uri': self.request.uri,
            'version': self.request.version,
            'remote_ip': self.request.remote_ip,
            'arguments': self.request.arguments,
            'body': self.request.body,
            'body_arguments': self.request.body_arguments,
            'headers': dict(self.request.headers)
        }
        return req_data

    def not_ok(self, msg: str, http_status: int = HTTPStatus.BAD_REQUEST, http_status_message: str | None = None, inner_excp: Any = None):
        '''
            Resposne NOT OK with Status and Message
        '''
        if http_status_message is not None:
            self.set_status(http_status, reason=http_status_message)
        else:
            self.set_status(http_status, reason=msg)

        self.write(HTTPBody(
            status_code_=http_status,
            status_message_=msg,
            data={} if inner_excp is None else str(inner_excp)
        ).body())

    def undefined_method_call(self, *args) -> None:
        '''
            Undefined Method Call
        '''
        self.not_ok(msg="Unsupported Request", inner_excp={"Args": args}, http_status=HTTPStatus.METHOD_NOT_ALLOWED)

    get = undefined_method_call
    head = undefined_method_call
    post = undefined_method_call
    delete = undefined_method_call
    patch = undefined_method_call
    put = undefined_method_call
    options = undefined_method_call
