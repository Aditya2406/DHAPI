'''
    vsrv - Application Server
'''
import ssl
import asyncio
import os
import sys
from typing import List, Final
import tornado.web
import tornado.httpserver
from colorama import Fore

from handlers.admins_handlers.admin_handler import AdminHandler
from handlers.artist_handlers.artist_auth_handler import ArtistAuthHandler
from handlers.artist_handlers.artist_handlers import ArtistHandler
from handlers.release_handler.release_handler import ReleaseHandler
from vsrv.utils import config_utils
from vsrv.models import config_keys
from vsrv.logging.insight import SystemInsight


class ExchangeAppServer():
    '''
        ARIS - Application Server
    '''

    # App Specific Variables
    Name: str = ''
    Version: Final[str] = '1.0.0'
    RootDirectoryPath: str = ''
    ConfigDirectoryPath: str = ''
    ConfigFileName: str = ''
    ConstantFileName: str = ''

    # App Instance
    ServerInstance: tornado.web.Application

    @staticmethod
    def init():
        '''
            arsrv - ARIS Server - INITIALIZE
        '''
        # ? Initialize Directory and File Paths
        ExchangeAppServer.Name = "VARIS Server"
        ExchangeAppServer.RootDirectoryPath = os.path.abspath("./")
        ExchangeAppServer.ConfigDirectoryPath = f'{ExchangeAppServer.RootDirectoryPath}/config'
        ExchangeAppServer.ConfigFileName = f'{ExchangeAppServer.ConfigDirectoryPath}/config.json'
        ExchangeAppServer.ConstantFileName = f'{ExchangeAppServer.ConfigDirectoryPath}/const.json'

    async def start(self, app_name: str = "Cache Server", app_port: int = 20000, ssl_context: ssl.SSLContext | None = None, app_debug: bool = False, app_auto_reload: bool = False):
        '''
            ARIS Server - START
        '''
        try:
            print(Fore.BLUE + f'\t{app_name} Server Application Loading', end="\n\n")
            ExchangeAppServer.Name = app_name
            ExchangeAppServer.ServerInstance = tornado.web.Application(
                handlers=APPLICATION_HANDLERS,
                template_path="handler_views",
                static_path=os.path.join(os.path.abspath(os.path.dirname(".")), "static"),
                compiled_template_cache=False,
                debug=app_debug,
                autoreload=app_auto_reload
            )
            ExchangeAppServer.ServerInstance.settings[config_keys.APP_CONFIGURATION_KEY] = config_utils.ConfigurationUtils.Configuration
            ExchangeAppServer.ServerInstance.settings[config_keys.APP_CONSTANT_KEY] = config_utils.ConfigurationUtils.Constant

            # ? Configure Tornado HTTP Server
            http_server: tornado.httpserver.HTTPServer
            if ssl_context is not None:
                http_server = tornado.httpserver.HTTPServer(
                    ExchangeAppServer.ServerInstance,
                    ssl_options=ssl_context
                )
            else:
                http_server = tornado.httpserver.HTTPServer(
                    ExchangeAppServer.ServerInstance
                )

            http_server.listen(
                port=app_port,
                reuse_port=True
            )

            if app_debug:
                print(Fore.YELLOW + f'\t{app_name} : Configuration', end="\n\n")
                # print(Fore.YELLOW + '\t\t' + config_utils.ConfigurationUtils.Configuration.to_json())

                print(Fore.CYAN + f'\t{app_name} : Constants', end="\n\n")
                # print(Fore.CYAN + '\t\t' + config_utils.ConfigurationUtils.Constant.to_json())

            # Application Info
            SystemInsight.logger().info(f'{config_utils.ConfigurationUtils.Constant.Application.Title} (ver. {config_utils.ConfigurationUtils.Constant.Application.Version}) Server Application - {config_utils.ConfigurationUtils.Constant.Application.Environment} - Started')

            # Starting Process
            await asyncio.Event().wait()
        except Exception as ex:
            print(Fore.RED + f'\t {app_name} Server Application - Exception Handled', end="\n\n")
            print(Fore.RED + str(ex))
            SystemInsight.logger().exception(msg=f'Exchange Application Failed, {str(ex)}')
            sys.exit(0)


# * URLs
# ? => Admin
# ? => Artists

#
APPLICATION_HANDLERS: Final[List] = [

    # ==> Admin
    # * GET | POST : Login Admin
    (r"/web/admin/login?", AdminHandler),
    (r"/web/admin/login/([A-Za-z0-9]*)/?", AdminHandler),



    # ==> Artists
    # * GET | POST : Create Artist
    (r"/web/artist/create/?", ArtistHandler),
    (r"/web/artist/create/([A-Za-z0-9]*)/?", ArtistHandler),

    # * GET | POST : Login Artist
    (r"/web/artist/login?", ArtistAuthHandler),
    (r"/web/artist/login/([A-Za-z0-9]*)/?", ArtistAuthHandler),

    # ==> Artists
    # * GET | POST : Create Artist
    (r"/web/release/create/([A-Za-z0-9]*)/", ReleaseHandler),
]
