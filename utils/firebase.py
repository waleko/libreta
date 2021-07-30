from typing import Union

import firebase_admin
from firebase_admin import credentials


class FirebaseUtils(object):
    """
    Utilities for firebase
    """

    @classmethod
    def setup_firebase(cls, certificate: Union[dict, str], databaseURL: str) -> None:
        """
        Initializes firebase

        :param certificate: Credentials as a dict or path to json file
        :param databaseURL: Realtime database url
        """
        cert = credentials.Certificate(certificate)
        firebase_admin.initialize_app(cert, {
            "databaseURL": databaseURL
        })
