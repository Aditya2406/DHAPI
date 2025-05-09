'''
    vsrv - Exchange Server - Engine Starter
'''
import importlib
import ssl
import os
import asyncio
import logging
import colorama
from colorama import Fore
from vsrv import app_server, app_server_test
from vsrv.utils import config_utils, core_utils
from vsrv.logging.insight import SystemInsight
from vsrv.models.system_models import SystemInitializationResult
from vsrv.exceptions import ApplicationException

# Clear Cache
importlib.invalidate_caches()

logging.basicConfig(level=logging.INFO)
__application_port: int = 20000
__ssl_context: ssl.SSLContext | None = None
__app_debug: bool = False


async def __initialize_system__() -> SystemInitializationResult | None:
    '''
        Initializes System
    '''

    # ? Clear Console
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

    # ? Before Everything
    colorama.init(autoreset=True)

    # ? Starting System
    print(Fore.LIGHTYELLOW_EX + '!!! <><>!!! <><> !!!', end="\n\n")
    print(Fore.GREEN + '<><> Cache <><> API SERVER <><>', end="\n")

    # ? Initial & Start Server async
    app_server.ExchangeAppServer.init()
    # ? Reading Server Constants

    try:
        config_utils.ConfigurationUtils.load_constant(app_server.ExchangeAppServer.ConstantFileName)
        print(Fore.GREEN + '\tServer Constant Loaded SUCCESSFULLY', end="\n")
    except Exception as ex:
        print(Fore.RED + '\tServer Constant Loading FAILED', end="\n")
        print(Fore.RED + str(ex))
        return None

    # ? Reading Server Configuration
    try:
        config_utils.ConfigurationUtils.load_config(app_server.ExchangeAppServer.ConfigFileName)
        print(Fore.GREEN + '\tServer Configuration Loaded SUCCESSFULLY', end="\n\n")
    except Exception as ex:
        print(Fore.RED + '\tServer Configuration Loading FAILED', end="\n")
        print(Fore.RED + str(ex))
        return None

    # ? Check Cloud Logging
    SystemInsight.logger().info("Configuration and Constants Loaded")

    # ? Check for Executing Arguments
    _args = core_utils.executing_arguments()
    SystemInsight.logger().info("Beginning Validation of Startup Arguments")

    # ? Validate Database Connection
    try:
        coll_names = await app_server_test.test_app_db_connect()
        SystemInsight.logger().info(f"Database Connection Test - Successful (found {len(coll_names)} Data Collections)")
    except ApplicationException:
        SystemInsight.logger().exception("Database Connection Test - Failed")
        return None
    except Exception:
        SystemInsight.logger().exception("Database Connection Test - Failed")
        return None

    # ? Preparing Server
    try:
        __application_port: int = 20000
        if "--port" in _args:
            try:
                __application_port = int(_args["--port"])
            except Exception as exc:
                print(Fore.RED + f'--port should be positive integer value less than 99999. Error : {str(exc)}')
        SystemInsight.logger().info(f"TCP Port : {__application_port}")

        __ssl_context: ssl.SSLContext | None = None
        if "--certificate" in _args and "--privatekey" in _args and "--ca_certificate" in _args:
            # * Configure SSL Context
            try:
                __ca_certificate: str = _args["--ca_certificate"]
                __certificate: str = _args["--certificate"]
                __privatekey: str = _args["--privatekey"]
                __ssl_context = ssl.create_default_context(
                    ssl.Purpose.CLIENT_AUTH,
                    cafile=__ca_certificate
                )
                __ssl_context.load_cert_chain(
                    certfile=__certificate,
                    keyfile=__privatekey,
                )
            except Exception as exc:
                __ssl_context = None
                print(Fore.RED + f'SSL Certificate Error : {str(exc)}')
        SystemInsight.logger().info(f"SSL Context : {'Yes' if __ssl_context is not None else 'No'}")

        __app_debug: bool = False
        if "--debug" in _args:
            if _args['--debug'] in ['True', 'False']:
                __app_debug = bool(_args["--debug"])
            else:
                __app_debug = False
                print(Fore.RED + 'Valid Values for --debug are True or False')
        SystemInsight.logger().info(f"Debug : {'Yes' if __app_debug else 'No'}")

        return SystemInitializationResult(ApplicationPort=__application_port, SecureContext=__ssl_context, AppDebug=__app_debug)

    except ApplicationException as app_exc:
        print(Fore.RED + '--- System Initialization Failed ---', end="\n\n")
        print(Fore.RED + app_exc.Message)
        SystemInsight.logger().exception(msg=f'System Initialization Failed, {app_exc.Message}')
        return None

    except Exception as app_exc:
        print(Fore.RED + '--- System Initialization Failed ---', end="\n\n")
        print(Fore.RED + str(app_exc))
        SystemInsight.logger().exception(msg=f'System Initialization Failed, {str(app_exc)}')
        return None


# Application Launcher 🚀
if __name__ == "__main__":
    # ? Preparing Server
    try:
        # ? Initialize System
        SIR: SystemInitializationResult | None = asyncio.run(__initialize_system__())

        # * Preparing Exchange Server
        if SIR is not None:
            MWA = app_server.ExchangeAppServer()
            asyncio.run(
                MWA.start(
                    app_port=SIR.ApplicationPort,
                    ssl_context=SIR.SecureContext,
                    app_debug=SIR.AppDebug,
                    app_auto_reload=True
                )
            )
    except ApplicationException as Ex:
        print(Fore.RED + '--- Application Exception ---', end="\n\n")
        print(Fore.RED + Ex.Message)
        SystemInsight.logger().exception(msg=f'Application Failed, {Ex.Message}')

    except Exception as Ex:
        print(Fore.RED + '--- System Level Exception ---', end="\n\n")
        print(Fore.RED + str(Ex))
        SystemInsight.logger().exception(msg=f'Application Failed, {str(Ex)}')
