'''
    vsys - Constant Configuration Model
'''
from dataclasses import dataclass, field


class EnvironmentTypes():
    '''
        Environment Types
    '''
    Development: str = "DEV"
    Test: str = "TEST"
    Production: str = "PROD"


@dataclass
class ApplicationConstant():
    '''
        Application Constant
    '''
    Title: str = field(default="")
    Version: str = field(default="")
    Environment: str = field(default=EnvironmentTypes.Development)
    SafeTitle: str = field(default="")
    SubTitle: str = field(default="")
    PublicPortal: str = field(default="")
    Currency: str = field(default="")
    CurrencySymbol: str = field(default="")
    OrangeMoneyServiceProviderCode: str = field(default="")
    AfriMoneyServiceProviderCode: str = field(default="")
    AirtelMoneyServiceProviderCode: str = field(default="")
    VodacomMoneyServiceProviderCode: str = field(default="")

    CCLAdminChannelCode: str = field(default="")

    ExternalGameTVBETCode: str = field(default="")
    ExternalGameTVBETParentCode: str = field(default="")


@dataclass
class SystemConstantModel():
    '''
        System Level Constant Model
    '''
    Application: ApplicationConstant = field(default_factory=ApplicationConstant)
