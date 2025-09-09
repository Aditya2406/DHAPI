"""
    Release Handlers
"""

import dataclasses
import json
import math
from platform import release
from typing import Final
from http import HTTPStatus
from bson import ObjectId
from pymongo.results import InsertOneResult
import bson
import bson.json_util
from handlers.artist_handlers.artist_auth_handler import ArtistAuthHandler
from handlers.soft_wallet_handler.soft_wallet_handler import SoftWalletTools
from vsrv import DatabaseCollections, DatabaseCollectionConnectionProvider
from vsrv.models.data_models.artist_data_model import ArtistDataModel, ArtistGender, ArtistSessionDataModel, ArtistTypes
from vsrv.models.data_models.release_data_model import ReleaseDataModel
from vsrv.models.request_models.artist_request_model import ArtistCreateRequestModel
from vsrv.models.request_models.release_create_model import RealeseCreateRequestModel
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

    async def _create_release(self, release_request: RealeseCreateRequestModel, artist_id: str,) -> ReleaseDataModel:
        """
        Create artist
        """
        # Create artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.RELEASES

        # check for duplicate
        existing_release_data = await dbcoll.find_one(
            filter={
                "ArtistId": ObjectId(artist_id),
                "Title": release_request.RealeseName,
                "Deleted": False,
            }
        )

        if existing_release_data is not None:
            raise ApplicationException(
                message="Release Title Already Exist",
                severity=ExceptionSeverity.LOW,
                reason=ExceptionReason.USER,
            )

        release_data = ReleaseDataModel()
        release_data.set_id(bson.ObjectId())
        release_data.Title = release_request.RealeseName
        release_data.ReleaseType = release_request.ReleaseType
        release_data.ArtistId = ObjectId(artist_id)
        release_data.Created = core_utils.now_utc()
        release_data.CreatedStr = core_utils.now_drc_str()
        release_data.Updated = core_utils.now_utc()
        release_data.UpdatedStr = core_utils.now_drc_str()

        artist_insert_result: InsertOneResult = await dbcoll.insert_one(
            document=dataclasses.asdict(release_data)
        )
        if artist_insert_result.acknowledged:
            return release_data
        else:
            raise ApplicationException(
                message="Unable to create Release",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
            )

    async def _get_artist_release(self, artist_id: str,) -> list:
        """
        Create artist
        """
        # Create artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.RELEASES

        # check for duplicate
        release_data = await dbcoll.find(
            filter={
                "ArtistId": ObjectId(artist_id),
                "Deleted": False,
            }
        ).to_list()

        return release_data

    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ! POST Method
    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def post(self, artist: str = ""):
        """
            Handle Post Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}: {artist} : RELEASE CREATE REQUEST"
        SystemInsight.logger().info(log_msg_heading)

        # Check Ticket Data and Save
        post_content = self.request.body
        json_pc = json.loads(post_content)

        release_create_request: RealeseCreateRequestModel
        try:

            release_create_request = RealeseCreateRequestModel(**json_pc)
            # await self.__validate_create_post_request__(artist_request=release_create_request)
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

            artist_session = await ArtistAuthHandler.validate_token_global(release_create_request.token)
            if artist_session is None:
                log_msg = f"{log_msg_heading} : Invalid Token"
                SystemInsight.logger().warning(log_msg)
                self.not_ok(
                    msg="Invalid Token", http_status=HTTPStatus.UNAUTHORIZED
                )
                return
            # create realese
            await self._create_release(release_request=release_create_request, artist_id=str(artist_session.ArtistOId))
            self.set_status(HTTPStatus.OK)
            _response_ = HTTPBody(
                status_code_=HTTPStatus.OK,
                status_message_="Release  Created Successfully",
                data={},
            )
            self.write(_response_.body())

        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Process Create  Release Request : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg="Unable to Process Release Artist Request ",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return

    async def get(self, artist: str = ""):
        """
            Handle Get Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}"
        if artist is not None and artist != "":
            log_msg_heading = (
                f"{log_msg_heading} : {artist} : GET ARTISTS Release REQUEST"
            )
        else:
            log_msg_heading = f"{log_msg_heading} : NEW ARTISTS Release REQUEST"
        # --
        SystemInsight.logger().info(log_msg_heading)

        try:
            if artist != "":
                releases = await self._get_artist_release(artist_id=artist)
                self.set_status(HTTPStatus.OK)
                _response_ = HTTPBody(
                    status_code_=HTTPStatus.OK,
                    status_message_="Artist Releases Retrieved Successfully",
                    data=json.loads(bson.json_util.dumps(releases)),
                )
                self.write(_response_.body())
                return
            else:
                log_msg = f"{log_msg_heading} : Unable to Get Artists Request : Please provide valid Arist Id"
                SystemInsight.logger().exception(msg=log_msg)
                self.not_ok(
                    msg="Please provide valid Arist Id",
                    http_status=HTTPStatus.BAD_REQUEST,
                )
                return

        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Get Artist : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg=f"Unable to Get Artist : {aexc.Message}",
                http_status=HTTPStatus.BAD_REQUEST,
            )
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Get Artists Request : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg="Unable to Get Artists Request ",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return
