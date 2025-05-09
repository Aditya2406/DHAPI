'''
    vSys - Configuration Utility
'''
import os
import json
import enum
from typing import Any
import motor
from motor.core import AgnosticDatabase, AgnosticClient
from colorama import Fore
from dacite import from_dict
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.models.config_models import ConfigurationModel, DBServerType, DBConfig
from vsrv.models.const_models import SystemConstantModel


class ConfigurationUtils():
    '''
        vsrv - Configuration Utility
    '''
    Configuration: ConfigurationModel
    Constant: SystemConstantModel

    @staticmethod
    def load_config(config_file: str):
        '''
            Load Configuration from ConfigFile
        '''
        if not os.path.exists(config_file):
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message=f"Configuration File : {config_file} NOT FOUND 😭"
            )
        if not os.path.isfile(config_file):
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message=f"Configuration File : {config_file} Path Found but as Directory, expecting as FILE 😔"
            )

        try:
            config_file_content = open(config_file, encoding="UTF-8").read()
            config_json_dict = json.loads(config_file_content)
            ConfigurationUtils.Configuration = from_dict(data_class=ConfigurationModel, data=config_json_dict)
        except Exception as exc:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                reason=ExceptionReason.SYSTEM,
                message="Exception Loading System Configuration",
                exceptionObject=exc
            ) from exc

    @staticmethod
    def load_constant(const_file: str):
        '''
            Load Constant from Constant File
        '''
        if not os.path.exists(const_file):
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message=f"Constant File : {const_file} NOT FOUND 😭"
            )
        if not os.path.isfile(const_file):
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message=f"Constant File : {const_file} Path Found but as Directory, expecting as FILE 😔"
            )

        try:
            const_file_content = open(const_file, encoding="UTF-8").read()
            const_json_dict = json.loads(const_file_content)
            ConfigurationUtils.Constant = from_dict(data_class=SystemConstantModel, data=const_json_dict)
        except Exception as exc:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                reason=ExceptionReason.SYSTEM,
                message="Exception Loading System Constant",
                exceptionObject=exc
            ) from exc


@staticmethod
def app_db_conn_str(db_config: DBConfig) -> str:
    '''
        Get Application Database Connection String
    '''
    __app_name__ = "ARIS"
    dbc: DBConfig = db_config
    if dbc.DatabaseServerType == DBServerType.MONGO_DB:
        db_conn_str = None
        # Setting App Name : STATIC
        options = []
        options.append(f"appName={__app_name__}")

        mongo_options = str.join("&", options)

        _server_port = dbc.ServerPort if dbc.ServerPort != "" else "27017"

        if (dbc.User == "" or dbc.User is None) and (dbc.Password == "" or dbc.Password is None):
            db_conn_str = f"mongodb://{dbc.Server}:{_server_port}/{dbc.Database}"
        else:
            db_conn_str = f"mongodb://{dbc.User}:{dbc.Password}@{dbc.Server}:{_server_port}/{dbc.Database}"

        return db_conn_str      # Return Connection String

    else:
        raise ApplicationException(
            severity=ExceptionSeverity.SHOW_STOPPER,
            message=f"Non Supported Database Configuration : {dbc.DatabaseServerType}"
        )
        # No Connection String


@staticmethod
def app_dbsrv_connect() -> AgnosticClient:
    '''
        Application Database Server Connect
    '''
    dbc: DBConfig = ConfigurationUtils.Configuration.DatabaseConfiguration
    if dbc.DatabaseServerType == DBServerType.MONGO_DB or dbc.DatabaseServerType == DBServerType.MONGO_DB_REPLICA_SET:
        db_con_str = app_db_conn_str(db_config=dbc)
        try:
            db_motor_con = motor.motor_tornado.MotorClient(db_con_str)
            return db_motor_con
        except Exception as exc:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message="Exception Making Connection with Server Database",
                exceptionObject=exc
            ) from exc
    else:
        print(Fore.RED + 'Invalid Log Database Server Type. Supported Database Types : MONGO_DB and MONGO_DB_REPLICA_SET')
        raise ApplicationException(
            severity=ExceptionSeverity.SHOW_STOPPER,
            message=f"Non Supported Database Configuration : {dbc.DatabaseServerType}"
        )


@staticmethod
def app_db_connect(db_motor_con: AgnosticClient | None = None) -> AgnosticDatabase:
    '''
        Application Database Connect
    '''
    dbc: DBConfig = ConfigurationUtils.Configuration.DatabaseConfiguration
    if dbc.DatabaseServerType == DBServerType.MONGO_DB or dbc.DatabaseServerType == DBServerType.MONGO_DB_REPLICA_SET:
        db_con_str = app_db_conn_str(db_config=dbc)
        try:
            # ? Check if Database Server Connection is already established
            if db_motor_con is None:
                db_motor_con = motor.motor_tornado.MotorClient(db_con_str)

            # ? Get Database Connection
            db_motor = db_motor_con[dbc.Database]
            return db_motor
        except Exception as exc:
            raise ApplicationException(
                severity=ExceptionSeverity.SHOW_STOPPER,
                message="Exception Making Connection with Server Database",
                exceptionObject=exc
            ) from exc
    else:
        print(Fore.RED + 'Invalid Log Database Server Type. Supported Database Types : MONGO_DB and MONGO_DB_REPLICA_SET')
        raise ApplicationException(
            severity=ExceptionSeverity.SHOW_STOPPER,
            message=f"Non Supported Database Configuration : {dbc.DatabaseServerType}"
        )


@staticmethod
def system_model_to_list(model: Any) -> list:
    '''
        System Model to List
    '''
    try:
        property_list = []
        for prop in model.__annotations__.items():
            property_name = prop[0]
            property_type = prop[1]
            if isinstance(property_type, enum.EnumMeta):
                property_list.append((property_name, model.getattr(property_name)))
            elif property_type is str or property_type is int or property_type is list:
                property_list.append((property_name, model.getattr(property_name)))
            else:
                inner_property_list = system_model_to_list(model.getattr(property_name))
                for prt in inner_property_list:
                    property_list.append((f'{property_name}_{prt[0]}', prt[1]))
        return property_list
    except Exception:
        return []
