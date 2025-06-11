"""
    Release Handlers
"""

import dataclasses
import json
import math
from typing import Final
from http import HTTPStatus
from pymongo.results import InsertOneResult
import bson
import bson.json_util
from handlers.soft_wallet_handler.soft_wallet_handler import SoftWalletTools
from vsrv import DatabaseCollections, DatabaseCollectionConnectionProvider
from vsrv.models.data_models.artist_data_model import ArtistDataModel, ArtistGender, ArtistTypes
from vsrv.models.request_models.artist_request_model import ArtistCreateRequestModel
from vsrv.models.response_models.artist_response_model import AgentsResponseModel, NewArtistsResponseModel
from vsrv.net.base_handlers import BaseRequestHandler
from vsrv.net.body import HTTPBody
from vsrv.logging.insight import SystemInsight
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.utils import json_utils, core_utils
from vsrv.utils.crypto_utils import encrypt_artist_key


class ReleaseHandler(BaseRequestHandler):
    """
        Release Handler
    """

    PRIMARY_COLLECTION_NAME: Final[str] = DatabaseCollections.ARTIST
    MEDIA_PATH: Final[str] = "static/tracks/"

    async def __validate_create_post_request__(self, artist_request: ArtistCreateRequestModel):
        """
        Validate Artist Request
        """
        log_msg = f"Validating Create Artist Request {artist_request.ArtistId} , {artist_request.ArtistName}"
        SystemInsight.logger().info(log_msg)

        if artist_request.Gender == ArtistGender.MALE or artist_request.Gender == ArtistGender.FEMALE or artist_request.Gender == ArtistGender.OTHERS:
            pass
        else:
            raise ApplicationException(
                message=f"Invalid artist Gender: {artist_request.Gender}"
                f'Must be one of Male : {ArtistGender.MALE}, Female : {ArtistGender.FEMALE}, Others : {ArtistGender.OTHERS}',
                severity=ExceptionSeverity.HIGH,
                reason=ExceptionReason.USER,
            )

        if len(artist_request.ArtistName) < 5:
            raise ApplicationException(
                message="Invalid artist Name",
                severity=ExceptionSeverity.HIGH,
                reason=ExceptionReason.USER,
            )

        if artist_request.BirthDate == "":
            raise ApplicationException(
                message="Invalid artist Date of Birth",
                severity=ExceptionSeverity.HIGH,
                reason=ExceptionReason.USER,
            )

    async def _create_artist(self, artist_request: ArtistCreateRequestModel, artist_key: str,) -> ArtistDataModel:
        """
        Create artist
        """
        # Create artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST

        # check for duplicate
        existing_artist_data = await dbcoll.find_one(
            filter={
                "ArtistId": artist_request.ArtistId,
                "Deleted": False,
            }
        )

        if existing_artist_data is not None:
            raise ApplicationException(
                message="Artist Already Exist",
                severity=ExceptionSeverity.LOW,
                reason=ExceptionReason.USER,
            )

        artist_data = ArtistDataModel()
        artist_data.set_id(bson.ObjectId())

        artist_data.ArtistId = artist_request.ArtistId
        artist_data.ArtistName = artist_request.ArtistName
        artist_data.ArtistContact = artist_request.ArtistContact
        artist_data.Key = encrypt_artist_key(artist_key)

        artist_data.Status = artist_request.Status

        artist_data.Gender = artist_request.Gender
        artist_data.BirthDate = artist_request.BirthDate

        artist_data.GeoLatitude = artist_request.GeoLatitude
        artist_data.GeoLongitude = artist_request.GeoLongitude
        artist_data.GeoLocation = artist_request.GeoLocation

        artist_data.Created = core_utils.now_utc()
        artist_data.CreatedStr = core_utils.now_drc_str()
        artist_data.Updated = core_utils.now_utc()
        artist_data.UpdatedStr = core_utils.now_drc_str()
        artist_data.ArtistType = ArtistTypes.FIELD_ARTIST

        artist_insert_result: InsertOneResult = await dbcoll.insert_one(
            document=dataclasses.asdict(artist_data)
        )
        if artist_insert_result.acknowledged:
            return artist_data
        else:
            raise ApplicationException(
                message="Unable to create Artist",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
            )

    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ! POST Method
    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def post(self, artist: str = ""):
        """
            Handle Post Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}: {artist} : TRACK CREATE REQUEST"
        SystemInsight.logger().info(log_msg_heading)

        # Check Ticket Data and Save
        post_content = self.request.body
        json_pc = json.loads(post_content)

        artist_create_request: ArtistCreateRequestModel
        try:
            artist_create_request = ArtistCreateRequestModel(**json_pc)
            await self.__validate_create_post_request__(artist_request=artist_create_request)
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Parse Create / Artist Request : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg=f"Unable to Parse Create / Artist Request : {aexc.Message}",
                http_status=HTTPStatus.BAD_REQUEST,
            )
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : INTERNAL SERVER ERROR - Unable to Process Create / Artist Request"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg=f"INTERNAL SERVER ERROR - Unable to Process Create / Artist Request : {str(exc)}",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return

        try:
            key = core_utils.generate_pin()
            if core_utils.CommonValidators.is_valid_mobile_number(artist_create_request.ArtistId) is False:
                log_msg = f"{log_msg_heading} : Invalid Artist ID"
                SystemInsight.logger().warning(log_msg)
                self.not_ok(
                    msg="Invalid Artist ID", http_status=HTTPStatus.BAD_REQUEST
                )
                return

            created_artist = await self._create_artist(
                artist_request=artist_create_request,
                artist_key=key
            )

            # Create the artist soft
            __artist_new_soft_wallet__ = (
                await SoftWalletTools.create_soft_wallet_for_artist_async(
                    artist_info=created_artist, method_msg=log_msg_heading
                )
            )
            if __artist_new_soft_wallet__ is not None:
                log_msg = f"{log_msg_heading} : Artist ID: {created_artist.ArtistName} : Soft Wallet Created"
                SystemInsight.logger().info(log_msg)

            _response_data_ = NewArtistsResponseModel()
            _response_data_.ArtistId = created_artist.get_id_str()
            _response_data_.ArtistUserName = created_artist.ArtistName
            _response_data_.Status = created_artist.Status
            _response_data_.Pin = key

            log_msg = f"{log_msg_heading} : Artist [{created_artist}] Created"
            SystemInsight.logger().info(msg=log_msg)
            self.set_status(HTTPStatus.OK)
            _response_ = HTTPBody(
                status_code_=HTTPStatus.OK,
                status_message_="Artist Created Successfully",
                data=dataclasses.asdict(_response_data_),
            )
            self.write(_response_.body())

        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Process Create  Artist Request : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg="Unable to Process Create Artist Request ",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return
