"""
    Artist Auth Handlers
"""

import dataclasses
import datetime
import json
from typing import Final
from http import HTTPStatus
from pymongo.results import InsertOneResult
import bson
import bson.json_util
from vsrv import DatabaseCollections, DatabaseCollectionConnectionProvider
from vsrv.models.data_models.artist_data_model import ArtistDataModel,  ArtistSessionDataModel
from vsrv.models.request_models.artist_login_request_model import ArtistLoginRequestModel
from vsrv.models.response_models.artist_login_response_handler import ArtistAuthToken, ArtistLoginResponseModel
from vsrv.net.base_handlers import BaseRequestHandler
from vsrv.net.body import HTTPBody
from vsrv.logging.insight import SystemInsight
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.utils import core_utils
from vsrv.utils.crypto_utils import encrypt_artist_key


class ArtistAuthHandler(BaseRequestHandler):
    """
        Channel Artist Handler
    """

    PRIMARY_COLLECTION_NAME: Final[str] = DatabaseCollections.ARTIST
    MEDIA_PATH: Final[str] = "static/artist_documents"

    async def _authenticate_artist(self, artist_req: ArtistLoginRequestModel) -> ArtistDataModel | None:
        """
            Authenticate artist by artistId, Key, and Channel Code
        """
        try:
            __db__ = DatabaseCollectionConnectionProvider()
            dbcoll = __db__.ARTIST

            artist_data = await dbcoll.find_one(
                filter={"ArtistId": artist_req.Username,
                        "Key": encrypt_artist_key(artist_req.Password),
                        "Deleted": False,
                        "Status": True})

            if artist_data is None:
                raise ApplicationException(message="Unable to Authenticate artist",
                                           severity=ExceptionSeverity.LOW,
                                           reason=ExceptionReason.USER)
            artist = ArtistDataModel(**artist_data)
            return artist

        except ApplicationException as aexc:
            log_msg = f"Authentication Failed : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Authentication Failed : {aexc.Message}",
                        http_status=HTTPStatus.UNAUTHORIZED)
            return None
        except Exception as exc:
            log_msg = "INTERNAL SERVER ERROR - Unable to Process artist Login Request"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"INTERNAL SERVER ERROR - Unable to Process artist Login Request : {str(exc)}",
                        http_status=HTTPStatus.BAD_REQUEST,
                        inner_excp=exc)
            return None

    async def _create_session_token(self, artist: ArtistDataModel, sessionid: str) -> ArtistSessionDataModel | None:
        """
            Create a Session Token for the artist
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST_SESSION_TOKENS

        existing_session = await dbcoll.find_one(
            filter={"SessionId": sessionid,
                    "artistId": artist.ArtistId,
                    "Deleted": False})
        if existing_session is not None:
            raise ApplicationException(message="Session Already Exist",
                                       severity=ExceptionSeverity.LOW,
                                       reason=ExceptionReason.USER)

        session_data = ArtistSessionDataModel()
        session_data.set_id(bson.ObjectId())
        session_data.ArtistId = artist.ArtistId
        session_data.SessionId = sessionid
        session_data.Created = core_utils.now_utc()
        session_data.CreatedStr = core_utils.now_utc_str()
        session_data.Updated = core_utils.now_utc()
        session_data.UpdatedStr = core_utils.now_utc_str()
        tokexp = core_utils.now_utc() + datetime.timedelta(hours=5)
        session_data.TokenExpiry = tokexp  # 5 hours from creation
        session_data.Deleted = False

        session_insert_result: InsertOneResult = await dbcoll.insert_one(document=dataclasses.asdict(session_data))

        if session_insert_result.acknowledged:
            return session_data
        else:
            raise ApplicationException(
                message="Unable to Create Session",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
            )

    @staticmethod
    async def _expire_artist_session(req: ArtistSessionDataModel) -> ArtistSessionDataModel:
        """
            Expire Token by comparing SessionId , AgenID, BusinessChannelID , TokenFor
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST_SESSION_TOKENS
        existing_session = await dbcoll.find_one(
            filter={
                "SessionId": req.SessionId,
                "TokenFor": req.TokenFor,
                "ArtistId": req.ArtistId,
                "Deleted": False,
            }
        )
        if existing_session is None:
            raise ApplicationException(
                message="Invalid Session | Session is already is Expired",
                severity=ExceptionSeverity.LOW,
                reason=ExceptionReason.INTEGRATION,
            )

        update_result = await dbcoll.update_one(
            filter={
                "SessionId": req.SessionId,
                "TokenFor": req.TokenFor,
                "ArtistId": req.ArtistId,
            },
            update={
                "$set": {
                    "Deleted": True,
                    "Updated": core_utils.now_utc(),
                    "UpdatedStr": core_utils.now_utc_str(),
                }
            },
        )

        if update_result.modified_count == 1:
            req.Deleted = True
            return req
        else:
            raise ApplicationException(
                message="Unable to expire the Session",
                severity=ExceptionSeverity.CRITICAL,
                reason=ExceptionReason.SYSTEM,
            )

    async def _validate_token(self, token: str) -> ArtistSessionDataModel:
        """
        Authenticate artist by artistId, Key, and Channel Code
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ARTIST_SESSION_TOKENS
        session_data = await dbcoll.find_one(
            filter={
                "_id": bson.ObjectId(token)
            }
        )
        if session_data is None:
            raise ApplicationException(
                message="Invalid token",
                severity=ExceptionSeverity.LOW,
                reason=ExceptionReason.USER,
            )
        session_data = ArtistSessionDataModel(**session_data)

        if core_utils.is_session_expired(session_data.TokenExpiry):
            session_data = await self._expire_artist_session(session_data)
        return session_data

    async def post(self):
        """
            Handle Post Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()} : Artist LOGIN REQUEST"
        SystemInsight.logger().info(log_msg_heading)

        login_request: ArtistLoginRequestModel
        try:
            post_content = self.request.body
            json_pc = json.loads(post_content)
            login_request = core_utils.to_dataclass(ArtistLoginRequestModel, json_pc)
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Parse Artist Login Request : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Unable to Parse artist Login Request : {aexc.Message}",
                        http_status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : INTERNAL SERVER ERROR - Unable to Process Artist Login Request"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"INTERNAL SERVER ERROR - Unable to Process Artist Login Request : {str(exc)}",
                        http_status=HTTPStatus.BAD_REQUEST,
                        inner_excp=exc)
            return

        # Authenticate the artist
        try:
            if core_utils.CommonValidators.is_valid_mobile_number(login_request.Username) is False:
                log_msg = f"{log_msg_heading} : Invalid Artist ID"
                SystemInsight.logger().warning(log_msg)
                self.not_ok(msg="Invalid Artist ID", http_status=HTTPStatus.BAD_REQUEST)
                return
            artist = await self._authenticate_artist(login_request)
            if artist is None:
                return
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Authentication Failed : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Authentication Failed : {aexc.Message}", http_status=HTTPStatus.UNAUTHORIZED)
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : INTERNAL SERVER ERROR - Unable to Authenticate artist"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg="INTERNAL SERVER ERROR - Unable to Authenticate artist",
                        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
                        inner_excp=exc)
            return

        # Create a session token for the artist
        session_token: ArtistSessionDataModel | None
        try:
            session_token = await self._create_session_token(artist, login_request.SessionId)
            if session_token is None:
                raise ApplicationException(message="Unable to Create Session Token",
                                           severity=ExceptionSeverity.CRITICAL,
                                           reason=ExceptionReason.SYSTEM)
            _response_data_ = ArtistLoginResponseModel()
            _response_data_.Token = session_token.get_id_str()
            _response_data_.ArtistId = artist.get_id_str()
            _response_data_.ArtistUserName = session_token.ArtistId
            _response_data_.ArtistFullName = artist.ArtistName
            _response_data_.TokenValidTill = str(session_token.TokenExpiry)
            _response_data_.TokenValidFor = session_token.TokenFor

            log_msg = f"{log_msg_heading} : artist [{login_request.Username}] Logged in Successfully, Session Token Created"
            SystemInsight.logger().info(msg=log_msg)
            self.set_status(HTTPStatus.OK)
            response = HTTPBody(status_code_=HTTPStatus.OK,
                                status_message_="Login Successful",
                                data=dataclasses.asdict(_response_data_))
            self.write(response.body())
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Create Session Token : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Unable to Create Session Token : {aexc.Message}",
                        http_status=HTTPStatus.GATEWAY_TIMEOUT)
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Create Session Token : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg="Unable to Create Session Token",
                        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
                        inner_excp=exc)
            return

    async def get(self, token: str = ""):
        """
        Handle Get Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()}"
        SystemInsight.logger().info(log_msg_heading)

        try:
            session = await self._validate_token(token)

            _response_data_ = ArtistAuthToken()
            _response_data_.Token = str(session.get_id())
            _response_data_.TokenValidTill = str(session.TokenExpiry)
            _response_data_.ArtistUserName = session.ArtistId
            _response_data_.TokenValidFor = session.TokenFor
            _response_data_.TokenExpired = session.Deleted

            log_msg = f"{log_msg_heading} : artist [{session.ArtistId}]  Token [{session.get_id()}] is Expired: {session.Deleted}"
            SystemInsight.logger().info(msg=log_msg)
            self.set_status(HTTPStatus.OK)
            status = "Valid Token"
            statcode = HTTPStatus.OK
            if session.Deleted:
                status = "Expired Token"
                statcode = HTTPStatus.NOT_FOUND

            response = HTTPBody(
                status_code_=statcode,
                status_message_=status,
                data=dataclasses.asdict(_response_data_),
            )
            self.write(response.body())

        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Get Business Channel artist : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg=f"Unable to Get Business Channel artist : {aexc.Message}",
                http_status=HTTPStatus.BAD_REQUEST,
            )
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Get Business Channel artist Request : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg="Unable to Get Business Channel artist Request ",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return
