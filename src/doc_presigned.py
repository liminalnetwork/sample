# Copyright 2025 Liminal Network
# See LICENSE for details

import json
from typing import Union
import urllib

from .shared import url, get_api_key

# --- Limited-use API keys, for including image links in transactional emails

__doc__ = """
This module defines one function:

    limited_use_key()

This allows you to "sign" a request, returning a "temporary" API key, which
can then be used to fetch information about a given shipment without needing
your API key. This is primarily used for embedding images in web pages, and
creating transactional email links:

    key = limited_use_key(
        scac,
        ["status", "proof", "lading", "image"],
        count=10, # caller can use this api key 10 times
        duration=7*86400 # the api key will last up to 1 week,
        pro=...
    )

    if isinstance(key, str):
        # this link can be used in a transactional email, allowing for users
        # to fetch the image without knowing your API key
        url = f"https://api.liminalnetwork.com/{scac}/proof?api_key={key}"
    else:
        raise Exception(key["errors])

"""


def limited_use_key(
    carrier: Union[str, int],
    methods: Union[list, tuple, set, str] = "status",
    count: int = 1,
    duration: int = 300,
    pro: str = None,
    bol: str = None,
    tracking: str = None,
) -> Union[str, dict]:
    """
    Args:

        carrier - numeric id of the carrier, as found from the /tracking page
        methods - sequence of strings, or comma-separated string of API methods
            to allow access to. Defaults to status, can include:
            status,date,lading,proof,rating
        count - number of times this can be accessed, 1 to 100, default 1
        duration - number of seconds this key should be valid, 1 to 2592000
            1 second to 1 month, default 300 = 5 minutes
        pro - pick one of pro, bol, or tracking, and provide your number
        bol - pick one of pro, bol, or tracking, and provide your number
        tracking - pick one of pro, bol, or tracking, and provide your number

    On success, returns:

        "Auth Key As string"

    On failure, returns:

        {"errors": [...]}

    """
    if not isinstance(methods, str):
        methods = ",".join(methods)
    methods = methods.replace("&", "")
    base = url.format(
        scac=carrier,
        method="sign",
        pro=pro,
        api_key=get_api_key(carrier),
    ) + (f"&methods={methods}&count={count}&duration={duration}")
    # provide one of pro=, bol=, or tracking=

    if not pro:
        # one of the other two should be valid
        rep = ("bol=" + bol) if bol else ("tracking=" + tracking)
        base = base.replace("pro=", rep, 1)

    ret = json.loads(urllib.request.urlopen(base).read().decode())
    if "auth" in ret:
        return ret["auth"]

    # there was an error
    return ret
