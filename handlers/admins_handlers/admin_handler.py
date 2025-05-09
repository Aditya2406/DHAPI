"""
    Admin Handlers
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
from vsrv.models.data_models.admin_data_model import AdminDataModel, AdminSessionDataModel
from vsrv.models.request_models.admin_login_request_model import AdminLoginRequestModel
from vsrv.models.response_models.admin_login_response_model import AdminsAuthToken, AdminsLoginResponseModel
from vsrv.net.base_handlers import BaseRequestHandler
from vsrv.net.body import HTTPBody
from vsrv.logging.insight import SystemInsight
from vsrv.exceptions import ApplicationException, ExceptionSeverity, ExceptionReason
from vsrv.utils import json_utils, core_utils


class AdminHandler(BaseRequestHandler):
    """
        Channel admin Handler
    """

    PRIMARY_COLLECTION_NAME: Final[str] = DatabaseCollections.ADMINS
    MEDIA_PATH: Final[str] = "static/admin_documents"

    @staticmethod
    async def __get_one(admin_id: str):
        """
            Get One admin
        """
        # Update admin Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINS
        admin_data = await dbcoll.find_one(
            filter={
                "_id": bson.ObjectId(admin_id),
            }
        )

        # Handle Id => CONVERT BSONID TO STRING
        srl_admin_data = json_utils.JSONHelper.odump_dict(admin_data)
        return srl_admin_data

    @staticmethod
    async def __get_many(record_skip: int, record_limit: int):
        """
        Get One admin
        """
        # Update admin Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINS

        admin_data = (
            await dbcoll.find(filter={})
            .skip(record_skip)
            .limit(record_limit)
            .to_list(length=record_limit)
        )

        # Handle Id => CONVERT BSONID TO STRING
        srl_admin_data = []
        for admin in admin_data:
            srl = json_utils.JSONHelper.odump_dict(admin)
            srl_admin_data.append(srl)

        return srl_admin_data

    @staticmethod
    async def __get_count():
        """
            Get Count of admins
        """
        # Update admin Data
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINS
        admin_data = await dbcoll.count_documents(filter={})
        return admin_data

    async def _authenticate_admin(self, admin_req: AdminLoginRequestModel) -> AdminDataModel | None:
        """
            Authenticate admin by adminId, Key, and Channel Code
        """
        try:
            __db__ = DatabaseCollectionConnectionProvider()
            dbcoll = __db__.ADMINS

            admin_data = await dbcoll.find_one(
                filter={"AdminId": admin_req.Username,
                        "Key": admin_req.Password,
                        "Deleted": False,
                        "Status": True})

            if admin_data is None:
                raise ApplicationException(message="Unable to Authenticate admin",
                                           severity=ExceptionSeverity.LOW,
                                           reason=ExceptionReason.USER)
            admin = AdminDataModel(**admin_data)
            return admin

        except ApplicationException as aexc:
            log_msg = f"Authentication Failed : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Authentication Failed : {aexc.Message}",
                        http_status=HTTPStatus.UNAUTHORIZED)
            return None
        except Exception as exc:
            log_msg = "INTERNAL SERVER ERROR - Unable to Process Admin Login Request"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"INTERNAL SERVER ERROR - Unable to Process Admin Login Request : {str(exc)}",
                        http_status=HTTPStatus.BAD_REQUEST,
                        inner_excp=exc)
            return None

    async def _create_session_token(self, admin: AdminDataModel, sessionid: str) -> AdminSessionDataModel | None:
        """
            Create a Session Token for the admin
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINTOKENS

        existing_session = await dbcoll.find_one(
            filter={"SessionId": sessionid,
                    "AdminId": admin.AdminId,
                    "Deleted": False})
        if existing_session is not None:
            raise ApplicationException(message="Session Already Exist",
                                       severity=ExceptionSeverity.LOW,
                                       reason=ExceptionReason.USER)

        session_data = AdminSessionDataModel()
        session_data.set_id(bson.ObjectId())
        session_data.AdminId = admin.AdminId
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
    async def _expire_admin_session(req: AdminSessionDataModel) -> AdminSessionDataModel:
        """
            Expire Token by comparing SessionId , AgenID, BusinessChannelID , TokenFor
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINTOKENS
        existing_session = await dbcoll.find_one(
            filter={
                "SessionId": req.SessionId,
                "TokenFor": req.TokenFor,
                "adminId": req.AdminId,
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
                "adminId": req.AdminId,
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

    async def _validate_token(self, token: str) -> AdminSessionDataModel:
        """
        Authenticate admin by adminId, Key, and Channel Code
        """
        __db__ = DatabaseCollectionConnectionProvider()
        dbcoll = __db__.ADMINTOKENS
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
        session_data = AdminSessionDataModel(**session_data)

        if core_utils.is_session_expired(session_data.TokenExpiry):
            session_data = await self._expire_admin_session(session_data)
        return session_data

    async def post(self):
        """
            Handle Post Call
        """
        log_msg_heading = f"{self.request.method}::{self.request.full_url()} : admin LOGIN REQUEST"
        SystemInsight.logger().info(log_msg_heading)

        login_request: AdminLoginRequestModel
        try:
            post_content = self.request.body
            json_pc = json.loads(post_content)
            login_request = core_utils.to_dataclass(AdminLoginRequestModel, json_pc)
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Unable to Parse admin Login Request : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Unable to Parse admin Login Request : {aexc.Message}",
                        http_status=HTTPStatus.BAD_REQUEST)
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : INTERNAL SERVER ERROR - Unable to Process admin Login Request"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"INTERNAL SERVER ERROR - Unable to Process admin Login Request : {str(exc)}",
                        http_status=HTTPStatus.BAD_REQUEST,
                        inner_excp=exc)
            return

        # Authenticate the Admin
        try:
            if core_utils.CommonValidators.is_valid_mobile_number(login_request.Username) is False:
                log_msg = f"{log_msg_heading} : Invalid admin ID"
                SystemInsight.logger().warning(log_msg)
                self.not_ok(msg="Invalid admin ID", http_status=HTTPStatus.BAD_REQUEST)
                return
            admin = await self._authenticate_admin(login_request)
            if admin is None:
                return
        except ApplicationException as aexc:
            log_msg = f"{log_msg_heading} : Authentication Failed : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg=f"Authentication Failed : {aexc.Message}", http_status=HTTPStatus.UNAUTHORIZED)
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : INTERNAL SERVER ERROR - Unable to Authenticate Admin"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(msg="INTERNAL SERVER ERROR - Unable to Authenticate Admin",
                        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
                        inner_excp=exc)
            return

        # Create a session token for the admin
        session_token: AdminSessionDataModel | None
        try:
            session_token = await self._create_session_token(admin, login_request.SessionId)
            if session_token is None:
                raise ApplicationException(message="Unable to Create Session Token",
                                           severity=ExceptionSeverity.CRITICAL,
                                           reason=ExceptionReason.SYSTEM)
            _response_data_ = AdminsLoginResponseModel()
            _response_data_.Token = session_token.get_id_str()
            _response_data_.AdminId = admin.get_id_str()
            _response_data_.AdminUserName = session_token.AdminId
            _response_data_.AdminFullName = admin.AdminName
            _response_data_.TokenValidTill = str(session_token.TokenExpiry)
            _response_data_.TokenValidFor = session_token.TokenFor

            log_msg = f"{log_msg_heading} : admin [{login_request.Username}] Logged in Successfully, Session Token Created"
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

            _response_data_ = AdminsAuthToken()
            _response_data_.Token = str(session.get_id())
            _response_data_.TokenValidTill = str(session.TokenExpiry)
            _response_data_.AdminUserName = session.AdminId
            _response_data_.TokenValidFor = session.TokenFor
            _response_data_.TokenExpired = session.Deleted

            log_msg = f"{log_msg_heading} : admin [{session.AdminId}]  Token [{session.get_id()}] is Expired: {session.Deleted}"
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
            log_msg = f"{log_msg_heading} : Unable to Get Business Channel admin : {aexc.Message}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg=f"Unable to Get Business Channel admin : {aexc.Message}",
                http_status=HTTPStatus.BAD_REQUEST,
            )
            return
        except Exception as exc:
            log_msg = f"{log_msg_heading} : Unable to Get Business Channel admin Request : {str(exc)}"
            SystemInsight.logger().exception(msg=log_msg)
            self.not_ok(
                msg="Unable to Get Business Channel admin Request ",
                http_status=HTTPStatus.BAD_REQUEST,
                inner_excp=exc,
            )
            return
