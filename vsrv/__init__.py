"""
    vsrv
"""

from typing import Final
from motor.core import AgnosticDatabase, AgnosticCollection, AgnosticClient
from vsrv.utils import config_utils
from .utils.class_utils import class_constants

# Constants

# ? Version Key
VERSION_KEY: Final[str] = "VERSION"

DB_COLLECTION_GAME_SERVICES = ""

# Classes


class DatabaseCollections:
    """
    Database Collections
    """

    ADMINS: Final[str] = "Admins"
    ADMINTOKENS: Final[str] = "AdminTokens"

    ARTIST: Final[str] = "Artists"
    ARTIST_SESSION_TOKENS: Final[str] = "ArtistsSessionTokens"
    SOFT_WALLETS: Final[str] = "SoftWallets"
    RELEASES: Final[str] = "Releases"

    # Release: Final[str] = "Release"


class DatabaseCollectionConnectionProvider:
    """
    Database Collections Connection Provider
    """

    def __init__(self):
        """
        Constructor
        """
        self.DatabaseServerConnection: AgnosticClient = config_utils.app_dbsrv_connect()
        self.DatabaseConnection: AgnosticDatabase = config_utils.app_db_connect(db_motor_con=self.DatabaseServerConnection)

    def get_collection(self, collection_name: str) -> AgnosticCollection:
        """
        Get Collection
        """
        return self.DatabaseConnection.get_collection(collection_name)

    def server_connection(self) -> AgnosticClient:
        """
        Get Server Connection
        """
        return self.DatabaseServerConnection

    @property
    def ADMINS(self) -> AgnosticCollection:
        """
        Get the name of the "BusinessChannels" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.ADMINS)

    @property
    def ADMINTOKENS(self) -> AgnosticCollection:
        """
        Get the name of the "BusinessChannels" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.ADMINTOKENS)

    @property
    def ARTIST(self) -> AgnosticCollection:
        """
        Get the name of the "BusinessChannels" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.ARTIST)

    @property
    def ARTIST_SESSION_TOKENS(self) -> AgnosticCollection:
        """
        Get the name of the "BusinessChannels" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.ARTIST_SESSION_TOKENS)

    @property
    def SOFT_WALLETS(self) -> AgnosticCollection:
        """
        Get the name of the "BusinessChannels" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.SOFT_WALLETS)

    @property
    def RELEASES(self) -> AgnosticCollection:
        """
        Get the name of the "RELEASES" collection.
        """
        return self.DatabaseConnection.get_collection(DatabaseCollections.RELEASES)
