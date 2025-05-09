'''
    System Models
'''
from dataclasses import dataclass, field
from ssl import SSLContext

class SystemHealthSeverityStates:
    '''
        System Health Severity
    '''
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SystemHealthStatusCodes:
    '''
        System Health Status Codes
    '''
    OK = 0
    SERVICE_UNAVAILABLE = 1

@dataclass
class SystemInitializationResult():
    '''
        System Initialization Result
    '''

    ApplicationPort: int = field(default_factory=int)

    SecureContext:SSLContext|None  = field(default=None)

    AppDebug:bool = field(default=False)

@dataclass
class SystemHealthStatus():
    '''
        System Health Status
    '''
    Name:str = field(default="")
    Status:int = field(default=SystemHealthStatusCodes.OK)
    StatusMessage:str = field(default="")
    Severity:str = field(default=SystemHealthSeverityStates.NONE)
    ExceptionMessage:str|None = field(default="")

@dataclass
class SystemHealthData():
    '''
        System Health
    '''
    HealthFactors: list[SystemHealthStatus]|None = field(default_factory=list)
