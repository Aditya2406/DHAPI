"""
    vSys - Utilities - Core Utilities
"""

import re
import sys
import datetime
from typing import Any
import random
import pytz
import dacite


from vsrv.exceptions import ApplicationException, ExceptionSeverity


def timezone_drc() -> datetime.tzinfo:
    """
    Africa - DRC - Kinshasha TimeZone
    """
    return pytz.timezone("Africa/Kinshasa")


def now_drc() -> datetime.datetime:
    """
    Africa - DRC - Current Time
    """
    return datetime.datetime.now(timezone_drc())


def now_drc_str() -> str:
    """
    Africa - DRC - Current Time in String
    """
    return now_drc().isoformat()


def now_utc() -> datetime.datetime:
    """
    Current UTC Time
    """
    return datetime.datetime.now(datetime.UTC)


def now_utc_str() -> str:
    """
    Current UTC Time in String
    """
    return now_utc().isoformat()


def to_dataclass(typ: type, val: Any) -> Any:
    """
    Try Convert to DataClass or raises Exception
    """
    try:
        return dacite.from_dict(data_class=typ, data=val)
    except Exception as exc:
        raise ApplicationException(
            message=str(exc), severity=ExceptionSeverity.HIGH
        ) from exc
    # *
    # *  ^^^ DO NO MODIFY EXCEPTION LOGIC ^^^
    # *


# ! Deprecated - 2024-10-29
# def json_to_dataclass(typ: type, val: Any) -> Any:
#     """
#     Try to  Convert JSON to Custom Data Class
#     """
#     return_obj = typ()

#     if typ.__name__ in ["str", "int", "float"]:
#         return_obj = typ(val)
#     else:
#         for fld in dc.fields(return_obj):
#             if (
#                 str(fld.type).startswith("str")
#                 or str(fld.type).startswith("int")
#                 or str(fld.type).startswith("float")
#             ):
#                 # if val.__contains__(fld.name):
#                 if fld.name in val:
#                     field_value = val[fld.name]
#                     if len(fld.type.__args__) > 0:
#                         field_value = fld.type.__args__[0](val[fld.name])
#                     setattr(return_obj, fld.name, field_value)

#             if str(fld.type).startswith("typing.List"):
#                 if fld.type._name == "List":
#                     if fld.name in val:
#                         field_value = val[fld.name]
#                         for field_value in field_value:
#                             if len(fld.type.__args__) > 0:
#                                 field_typed_value = json_to_dataclass(
#                                     fld.type.__args__[0], field_value
#                                 )
#                                 getattr(return_obj, fld.name).append(field_typed_value)
#                             else:
#                                 getattr(return_obj, fld.name).append(field_value)
#     return return_obj


def executing_arguments():
    """
    Returns Dictionary of Executing Arguments
    """
    _args = {}
    for arg in sys.argv[1:]:
        if "=" in arg:
            akv = arg.split("=")
            _args[akv[0]] = akv[1]
        else:
            _idx = str(sys.argv.index(arg))
            _args[_idx] = arg
    return _args


def get_regex_validator(regex_type: str):
    """
    Returns Regex Validator
    """
    if regex_type == "fullname":
        return r"^[a-zA-Z]+(([',. -][a-zA-Z ])?[a-zA-Z]*)*$"
    elif regex_type == "mobile":
        return r"^\+?[0-9]{10,15}$"
    elif regex_type == "drc_mobile":
        return r"^\+?243[0-9]{9}$"
    elif regex_type == "email":
        return r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    elif regex_type == "isodate":
        return r"^\d{4}-\d{2}-\d{2}$"
    else:
        raise ApplicationException(
            message="Invalid Regex Type", severity=ExceptionSeverity.HIGH
        )


class CommonValidators:
    """
    Regex Validation
    """

    @staticmethod
    def regex_validate_fullname(fullname: str):
        """
        Validate Full Name
        """
        return re.match(get_regex_validator("fullname"), fullname)

    @staticmethod
    def regex_validate_mobile(mobile_number: str):
        """
        Validate Mobile Number
        """
        return re.match(get_regex_validator("mobile"), mobile_number)

    @staticmethod
    def regex_validate_drc_mobile(mobile_number: str):
        """
        Validate DRC Mobile Number
        """
        return re.match(get_regex_validator("drc_mobile"), mobile_number)

    @staticmethod
    def is_valid_mobile_number(number: str) -> bool:
        '''
            Validate Mobile Number
        '''
        # Define the regex pattern
        pattern = r'^\+?91[0-9]{10}$'

        # Use re.match to check if the number matches the pattern
        return bool(re.match(pattern, number))

    @staticmethod
    def regex_validate_email(email: str):
        """
        Validate Email
        """
        return re.match(get_regex_validator("email"), email)

    @staticmethod
    def regex_validate_isodate(date: str):
        """
        Validate ISO Date
        """
        return re.match(get_regex_validator("isodate"), date)

    @staticmethod
    def validate_18plus(date: str):
        """
        Validate 18+ Date
        """
        if CommonValidators.regex_validate_isodate(date):
            __now__ = now_utc()
            __dob__ = datetime.datetime.strptime(date, "%Y-%m-%d").replace(
                tzinfo=pytz.utc
            )
            return (__now__ - __dob__).days > 6570
        else:
            return False

    @staticmethod
    def validate_password_strength(pswd: str) -> bool:
        r"""
        Validate Password Strength
            1.	^: Start of the string.
            2.	(?=.*[A-Za-z\d@$!%*#?&]): Ensures at least one character from the allowed set (letters, digits, special characters).
            3.	[A-Za-z\d@$!%*#?&]{5,16}: Matches 5 to 16 characters including alphabets, digits, or special characters.
            4.	$: End of the string.
        """
        __r__ = r"^(?=.*[A-Za-z\d@$!%*#?&])[A-Za-z\d@$!%*#?&]{5,16}$"
        return True if re.match(__r__, pswd) else False

    @staticmethod
    def validate_password_strength_strong(pswd: str):
        r"""
        Validate Password Strength
            1.	^: Start of string.
            2.	(?=.*[a-z]): Ensures at least one lowercase letter.
            3.	(?=.*[A-Z]): Ensures at least one uppercase letter.
            4.	(?=.*\d): Ensures at least one digit.
            5.	(?=.*[@$!%*#?&]): Ensures at least one special character from the specified set.
            6.	[A-Za-z\d@$!%*#?&]+: Matches one or more of the specified characters.
            7.	$: End of string.
        """
        __r__ = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]+$"
        return True if re.match(__r__, pswd) else False

    @staticmethod
    def validate_month(month):
        """
            Validate Month
        """
        return 1 <= month <= 12

    @staticmethod
    def validate_year(year):
        """
            Validate Month
        """
        return year > 0


def is_session_expired(expiry_time: datetime.datetime | None) -> bool:
    """
    Check UTC time for User
    """
    if expiry_time is None:
        return False

    current_time = now_utc()

    # Ensure expiry_time is timezone-aware
    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=datetime.UTC)
    else:
        expiry_time = expiry_time.astimezone(datetime.UTC)

    return current_time > expiry_time


def is_vsecure_session_expired(expiry_time: datetime.datetime | None) -> bool:
    """
    Check UTC time for Vsecure User
    """
    if expiry_time is None:
        return False

    current_time = now_utc()

    # Ensure expiry_time is timezone-aware
    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=datetime.UTC)

    return current_time > expiry_time


def generate_pin() -> str:
    """
    Generation 6 digits Pin
    """
    return str(random.randint(100000, 999999))
