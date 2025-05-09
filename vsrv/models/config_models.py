'''
    vsrv - Configuration Models
'''
from dataclasses import dataclass, field


class DBServerType:
    '''
        Configuration - Database Server Type
    '''
    MONGO_DB = "MONGO_DB"
    MONGO_DB_REPLICA_SET = "MONGO_DB_REPLICA_SET"


@dataclass
class DBConfig():
    '''
        Configuration - Database Configuration
    '''
    Status: str = field(default="Inactive")
    DatabaseServerType: str = field(default=DBServerType.MONGO_DB)
    ReplicaSet: str | None = field(default="")
    Server: str = field(default="")
    ServerPort: int | None = field(default=27017)
    User: str | None = field(default="")
    Password: str | None = field(default="")
    Database: str = field(default="")
    AuthDatabase: str | None = field(default="")


@dataclass
class AWSConfig():
    '''
        AWS API Configuration
    '''
    AccessId: str = field(default="")
    AccessSecret: str = field(default="")
    Region: str = field(default="")


@dataclass
class AWSCloudWatch():
    '''
        AWS Cloud Watch
    '''
    Status: str = field(default="Inactive")
    LogRetentionPeriod: int = field(default=120)


@dataclass
class ShellLoggingConfig():
    '''
        Shell Logging Configuration
    '''
    Status: str = field(default="Inactive")


@dataclass
class FileLoggingConfig():
    '''
        File Logging Configuration
    '''
    Status: str = field(default="Inactive")
    LogDirectory: str = field(default="")


@dataclass
class LoggingConfigurations():
    '''
        System Logging Configuration
    '''
    LogName: str = field(default="")
    ShellLog: ShellLoggingConfig = field(default_factory=ShellLoggingConfig)
    FileLog: FileLoggingConfig = field(default_factory=FileLoggingConfig)
    DatabaseLog: DBConfig = field(default_factory=DBConfig)
    AWSCloudWatchLog: AWSCloudWatch = field(default_factory=AWSCloudWatch)


@dataclass
class ConfigurationModel():
    '''
        Configuration Model
    '''
    DatabaseConfiguration: DBConfig = field(default_factory=DBConfig)
