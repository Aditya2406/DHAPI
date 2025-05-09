'''
    vSRV SoftWallet Models
'''
from dataclasses import dataclass, field
from datetime import datetime
from typing import Final
from bson import ObjectId
from .base_data_model import BaseDataModel, BaseFieldMeta


class SoftWalletTransactionType:
    '''
        Soft Wallet Transaction Codes
    '''
    NO_TRANSACTION: Final[int] = -1
    ENQUIRY: Final[int] = 0

    DEPOSIT: Final[int] = 100
    DEPOSIT_WINNING: Final[int] = 101
    # ! DEPOSIT_FOR_SALE: Final[int] = 102
    DEPOSIT_FOR_JOINING: Final[int] = 103
    DEPOSIT_BY_MOBILE_WALLET: Final[int] = 104
    # DEPOSIT_BY_RETAIL: Final[int] = 105
    DEPOSIT_FOR_CAMPAIGN: Final[int] = 199

    WITHDRAW: Final[int] = 200
    WITHDRAW_WINNING: Final[int] = 201
    WITHDRAW_FOR_SALE: Final[int] = 202

    # ! WITHDRAW_FOR_JOINING: Final[int] = 203
    WITHDRAW_TO_MOBILE_WALLET: Final[int] = 204
    WITHDRAW_TO_RETAIL: Final[int] = 205
    WITHDRAW_FOR_CAMPAIGN: Final[int] = 299

    FUNDING: Final[int] = 300
    REFUNDING: Final[int] = 301

    CHANNEL_FUNDING: Final[int] = 310
    CHANNEL_DEPLETE: Final[int] = 311

    CHANNEL_AGENT_FUNDING: Final[int] = 320
    CHANNEL_AGENT_DEPLETE: Final[int] = 321
    CHANNEL_AGENT_COMMISSION: Final[int] = 330

    RETAIL_ENCASH: Final[int] = 400

    REFUND: Final[int] = 500  # For Player, Agents


class SoftWalletReferenceType:
    '''
        Soft Wallet Reference Types
    '''
    ENCASH_REFERENCE: Final[int] = -2
    NO_REFERENCE: Final[int] = -1
    ARTIST_REFERENCE: Final[int] = 100


class SoftWalletPaymentTransactionStatus:
    '''
        Soft Wallet Payment Transaction Status
    '''
    INITIAL = 'INITIAL'
    IN_PROGRESS = 'IN_PROGRESS'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    CANCLED = 'CANCLED'


@dataclass
class SoftWalletTransactionModel(BaseDataModel):
    '''
        Soft Wallet Transaction Model
    '''
    ChannelId: ObjectId | None = field(default=None)
    ChannelCode: str = field(default_factory=str)

    TransactionGroupId: ObjectId | None = field(default=None)
    TransactionType: int = field(default=SoftWalletTransactionType.NO_TRANSACTION)
    TransactionPin: str = field(default_factory=str)

    PaymentVia: str | None = field(default=None)
    PaymentRequest: dict | None = field(default=None)
    PaymentResponse: dict | None = field(default=None)
    PaymentStatus: str | None = field(default=None)
    PaymentCurrency: str | None = field(default=None)

    DebitAccountId: ObjectId | None = field(default=None)
    DebitAccountType: int = field(default=SoftWalletReferenceType.NO_REFERENCE)
    DebitAccountOpeningBalanceTotal: int | None = field(default=None)
    DebitAccountOpeningBalanceReserved: int | None = field(default=None)
    DebitAccountOpeningBalanceAvailable: int | None = field(default=None)
    DebitAccountOpeningBalanceCommission: int | None = field(default=None)
    DebitAccountClosingBalanceTotal: int | None = field(default=None)
    DebitAccountClosingBalanceReserved: int | None = field(default=None)
    DebitAccountClosingBalanceAvailable: int | None = field(default=None)
    DebitAccountClosingBalanceCommission: int | None = field(default=None)

    CreditAccountId: ObjectId | None = field(default=None)
    CreditAccountType: int = field(default=SoftWalletReferenceType.NO_REFERENCE)
    CreditAccountOpeningBalanceTotal: int | None = field(default=None)
    CreditAccountOpeningBalanceReserved: int | None = field(default=None)
    CreditAccountOpeningBalanceAvailable: int | None = field(default=None)
    CreditAccountOpeningBalanceCommission: int | None = field(default=None)
    CreditAccountClosingBalanceTotal: int | None = field(default=None)
    CreditAccountClosingBalanceReserved: int | None = field(default=None)
    CreditAccountClosingBalanceAvailable: int | None = field(default=None)
    CreditAccountClosingBalanceCommission: int | None = field(default=None)

    TicketId: ObjectId | None = field(default=None)

    Reference: str = field(default_factory=str)
    Description: str = field(default_factory=str)

    Amount: int = field(default_factory=int)
    AmountOriginal: float = field(default_factory=float)

    CampaignApplied: bool = field(default_factory=bool)
    CampaignAppliedEvent: str | None = field(default=None)
    CampaignAppliedStatus: str | None = field(default=None)
    CampaignId: ObjectId | None = field(default=None)
    CampaignCode: str | None = field(default_factory=str)
    CampaignDiscount: float = field(default_factory=float)
    CampaignAffiliateId: ObjectId | None = field(default=None, metadata=BaseFieldMeta(is_secured=True).as_dict())
    CampaignAffiliateCode: str | None = field(default_factory=str, metadata=BaseFieldMeta(is_secured=True).as_dict())
    CampaignAffiliateBenefit: float = field(default_factory=float, metadata=BaseFieldMeta(is_secured=True).as_dict())
    Remarks: str | None = field(default=None)

    Status: bool = True
    StatusMessage: str = field(default_factory=str)

    Settled: bool = field(default=False)
    SettledBy: str | None = field(default_factory=str)
    SettledDate: datetime | None = field(default=None)
    SettledDateStr: str | None = field(default=None)
    SettledMessage: str | None = field(default=None)

    GeoLatitude: float | None = field(default=None)
    GeoLongitude: float | None = field(default=None)
    GeoLocation: str | None = field(default=None)


@dataclass
class SoftWalletModel(BaseDataModel):
    '''
        Soft Wallet Model
    '''
    ReferenceId: ObjectId | None = field(default=None)
    ReferenceCode: str = field(default_factory=str)
    ReferenceType: int = field(default=SoftWalletReferenceType.NO_REFERENCE)
    BalanceTotal: int = 0
    BalanceReserved: int = 0
    BalanceAvailable: int = 0
    BalanceCommission: int = 0
    WalletKey: str | None = field(default_factory=str, metadata=BaseFieldMeta(is_secured=True).as_dict())
    Status: bool = True
    StatusMessage: str = field(default_factory=str)
    CanWithdraw: bool = False
    CanDeposit: bool = True
    CanPlay: bool = True
