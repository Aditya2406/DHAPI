"""
    Artist Handlers
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


class ArtistHandler(BaseRequestHandler):
    """
        Channel artist Handler
    """

    PRIMARY_COLLECTION_NAME: Final[str] = DatabaseCollections.ARTIST
    MEDIA_PATH: Final[str] = "static/artist_documents"

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

    async def __get_one(self, artist_id: str):
        """
            Get One artist
        """
        # Update artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST
        artist_data = await dbcoll.find_one(
            filter={
                "_id": bson.ObjectId(artist_id),
            }
        )

        # Handle Id => CONVERT BSONID TO STRING
        srl_artist_data = json_utils.JSONHelper.odump_dict(artist_data)
        return srl_artist_data

    async def __get_many(self, record_skip: int, record_limit: int):
        """
        Get One artist
        """
        # Update artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST

        artist_data = (
            await dbcoll.find(filter={})
            .skip(record_skip)
            .limit(record_limit)
            .to_list(length=record_limit)
        )

        # Handle Id => CONVERT BSONID TO STRING
        srl_artist_data = []
        for artist in artist_data:
            srl = json_utils.JSONHelper.odump_dict(artist)
            srl_artist_data.append(srl)

        return srl_artist_data

    async def __get_count(self):
        """
            Get Count of Artists
        """
        # Update artist Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST
        artist_data = await dbcoll.count_documents(filter={})
        return artist_data

    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ! POST Method
    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

    async def post(self, artist: str = ""):
        """
            Handle Post Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}: {artist} : CREATE REQUEST"
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

    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    # ! POST Method
    # ! --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    async def get(self, artist: str = ""):
        """
            Handle Get Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}"
        if artist is not None and artist != "":
            log_msg_heading = (
                f"{log_msg_heading} : {artist} : GET ARTISTS REQUEST"
            )
        else:
            log_msg_heading = f"{log_msg_heading} : NEW ARTISTS REQUEST"
        # --
        SystemInsight.logger().info(log_msg_heading)

        try:
            if artist != "":
                artist_data = await self.__get_one(artist_id=artist)
                _response_data_ = AgentsResponseModel()
                _response_data_.Artists.append(artist_data)
                _response_data_.PageNumber = 1
                _response_data_.PageSize = 1
                _response_data_.TotalPages = 1

                log_msg = f"{log_msg_heading} : Artist [{artist}] Retrieved"
                SystemInsight.logger().info(msg=log_msg)
                self.set_status(HTTPStatus.OK)
                _response_ = HTTPBody(
                    status_code_=HTTPStatus.OK,
                    status_message_="Artist Retrieved",
                    data=dataclasses.asdict(_response_data_),
                )
                self.write(_response_.body())
            else:
                _page_no_ = self.get_argument("pageno", default="1")
                _page_size_ = self.get_argument("pagesize", default="5")
                _record_skip_ = 0
                _record_limit_ = 0
                # Calculate Page
                pageno_ = int(_page_no_) if _page_no_.isdigit() else 1
                pagesize_ = int(_page_size_) if _page_size_.isdigit() else 5
                _record_skip_ = (pageno_ - 1) * pagesize_
                _record_limit_ = pagesize_

                artists_count = await self.__get_count()
                artists_data = await self.__get_many(record_skip=_record_skip_, record_limit=_record_limit_)

                _response_data_ = AgentsResponseModel()
                _response_data_.Artists.append(artists_data)
                _response_data_.PageNumber = pageno_
                _response_data_.PageSize = pagesize_
                _response_data_.TotalPages = math.ceil(artists_count / pagesize_)

                log_msg = f"{log_msg_heading} : Artists [{len(artists_data)}] Retrieved"
                SystemInsight.logger().info(msg=log_msg)
                self.set_status(HTTPStatus.OK)
                _response_ = HTTPBody(
                    status_code_=HTTPStatus.OK,
                    status_message_="Artists Retrieved",
                    data=dataclasses.asdict(_response_data_),
                )
                self.write(_response_.body())

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

    @staticmethod
    async def get_by_id_async(artist_id: str) -> ArtistDataModel | None:
        """
            Get Artist By Id
        """
        # Update artist Data
        try:
            dbcoll = DatabaseCollectionConnectionProvider().get_collection(
                ArtistHandler.PRIMARY_COLLECTION_NAME
            )
            artist_data = await dbcoll.find_one(
                filter={
                    "_id": bson.ObjectId(artist_id)
                }
            )

            if artist_data is None:
                return None
            else:
                artist = ArtistDataModel(**artist_data)
                return artist
        except Exception:
            return None

    @staticmethod
    async def get_by_artistid_async(artist_id: str) -> ArtistDataModel | None:
        """
            Get artist By artistId
        """
        # Update artist Data
        dbcoll = DatabaseCollectionConnectionProvider().get_collection(
            ArtistHandler.PRIMARY_COLLECTION_NAME
        )
        artist_data = await dbcoll.find_one(
            filter={
                "ArtistId": artist_id,
            }
        )

        if artist_data is None:
            return None
        else:
            artist = ArtistDataModel(**artist_data)
            return artist
