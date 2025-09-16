# -*- coding: utf-8 -*-
from requests.adapters import HTTPAdapter

import ssl


class AddedCipherAdapter(HTTPAdapter):
    """
    This is needed because some websites (e.g. bassareggiana.it) are using old tls versions.
    This is a workaround to decrease the security level of the connection.
    """

    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        kwargs["ssl_context"] = context
        super().init_poolmanager(*args, **kwargs)
