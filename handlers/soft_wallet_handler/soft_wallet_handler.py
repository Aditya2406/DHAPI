'''
     Artist Soft Wallet Handlers
'''
from dataclasses import asdict
from typing import Final
import bson
import bson.json_util
import bson.objectid
from vsrv import DatabaseCollections, DatabaseCollectionConnectionProvider
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.logging.insight import SystemInsight
from vsrv.models.data_models.artist_data_model import ArtistDataModel
from vsrv.models.data_models.soft_wallet_data_models import SoftWalletModel, SoftWalletReferenceType
from vsrv.utils import core_utils, crypto_utils


class SoftWalletTools():
    '''
        Soft Wallet Handler
    '''
    PRIMARY_COLLECTION_NAME: Final[str] = DatabaseCollections.SOFT_WALLETS

    # *
    # * *** CREATE ***
    # *
    ### ! *** PUBLIC METHOD : CREATE SOFT WALLET - Artist [async] *** ! ###
    @staticmethod
    async def create_soft_wallet_for_artist_async(artist_info: ArtistDataModel, method_msg: str) -> dict:
        '''
            Create Artist Soft Wallet
        '''
        log_msg_heading = f'{method_msg} : CREATE SOFT WALLET REQUEST'
        SystemInsight.logger().info(log_msg_heading)

        # Validate Artist
        if artist_info is None:
            log_msg_heading = f'{method_msg} : CREATE Artist SOFT WALLET REQUEST : Artist Not Found'
            SystemInsight.logger().warning(log_msg_heading)
            raise ApplicationException(
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
                message="Artist Not Found"
            )
            # <-- FAIL
        else:
            # Check if Wallet Exists
            dbcoll = DatabaseCollectionConnectionProvider().get_collection(collection_name=DatabaseCollections.SOFT_WALLETS)
            wallet_filter = {
                "ReferenceType": SoftWalletReferenceType.ARTIST_REFERENCE,
                "ReferenceCode": artist_info.ArtistId,
                "ReferenceId": artist_info.get_id(),
                "Deleted": False,
                "Status": True
            }
            wallet_data = await dbcoll.find_one(filter=wallet_filter)

            # Check if Wallet Exists
            if wallet_data is not None:
                log_msg_heading = f'{method_msg} : CREATE Artist SOFT WALLET REQUEST : ALREADY FOUND'
                SystemInsight.logger().info(log_msg_heading)
                return wallet_data
                # --> SUCCESS
            else:
                # Create Soft Wallet for Artist
                new_wallet = SoftWalletModel(
                    ReferenceCode=artist_info.ArtistId,
                    ReferenceId=artist_info.get_id(),
                    ReferenceType=SoftWalletReferenceType.ARTIST_REFERENCE,
                    BalanceTotal=0,
                    BalanceReserved=0,
                    BalanceAvailable=0,
                    WalletKey=crypto_utils.encrypt_artist_key(artist_info.ArtistId[-4:]),
                    Status=True,
                    StatusMessage="New Wallet",
                    CanWithdraw=False,
                    CanDeposit=True,
                    CanPlay=True,
                    Created=core_utils.now_utc(),
                    CreatedStr=core_utils.now_drc_str(),
                    Updated=core_utils.now_utc(),
                    UpdatedStr=core_utils.now_drc_str()
                )
                new_wallet.set_id(bson.ObjectId())
                new_wallet_dict = asdict(new_wallet)
                new_created_wallet = await dbcoll.insert_one(document=new_wallet_dict)
                if new_created_wallet is not None:
                    log_msg_heading = f'{method_msg} : CREATE Artist SOFT WALLET REQUEST : CREATED SUCCESSFULLY'
                    SystemInsight.logger().info(log_msg_heading)
                    return new_wallet_dict
                    # --> SUCCESS
                else:
                    log_msg_heading = f'{method_msg} : CREATE Artist SOFT WALLET REQUEST : FAILED'
                    SystemInsight.logger().warning(log_msg_heading)
                    raise ApplicationException(
                        severity=ExceptionSeverity.CRITICAL,
                        reason=ExceptionReason.SYSTEM,
                        message="Unable to Create Artist Wallet"
                    )
                    # <-- FAIL
