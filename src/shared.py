# Copyright 2025 Liminal Network
# See LICENSE for details

import json
from typing import Union
import urllib.parse
import urllib.request

__doc__ = """
This module includes functions shared by other portions of this client
implementation.

"""

url = "https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}"
ebol_url = "https://api.liminalnetwork.com/{scac}/ebol_21"
pickup_url = "https://api.liminalnetwork.com/{scac}/pickup"
tender_url = "https://api.liminalnetwork.com/{scac}/tender"
rating_url = "https://api.liminalnetwork.com/{scac}/rating"
rating_schema_url = "https://account.liminalnetwork.com/rating.schema/"
supported_url = "https://api.liminalnetwork.com/supported?"
schema_url = "https://api.liminalnetwork.com/schema?name="


class settings:
    """overridden by `doc_client` when `doc_client` imports this module"""


def get_api_key(scac_or_carrier_id: str) -> str:
    """
    Args:

        scac_or_carrier_id - will use the mapping defined on
            settings.CARRIER_TO_CONFIG to discover the proper API key to use.

    Returns:

        "...api key..."
    """
    # LN gets LIMINAL_NETWORK_FINAL_MILE_API_KEY
    # SANDBOX gets KNOWN_SANDBOX_KEY
    # everything else gets LIMINAL_NETWORK_API_KEY
    if scac_or_carrier_id in settings.CARRIER_TO_CONFIG:
        return getattr(settings, settings.CARRIER_TO_CONFIG[scac_or_carrier_id])
    return getattr(settings, settings.CARRIER_TO_CONFIG[""])


# --- schema and supported method calls for /ebol_21 and /pickup


def get_schema(name: str = "list") -> Union[tuple, list]:
    """
    Args:

        name - {scac}.{api}.{http method}

    Returns:

        If the name provided is "list", will return:
            [name, name, ...]


        If name was previously returned by get_schema(), or was listed:
        https://account.liminalnetwork.com/account/carriers-schemas
        Will return:
            (json_schema, last_modified)

    """

    url = schema_url

    if name.partition(".")[0].isdigit():
        raise ValueError(
            "cannot verify API existence with numeric carrier_id, please use the SCAC instead"
        )

    if name.endswith(".rating.post"):
        # rating uses a different type schema
        name = name.partition(".")[0]
        url = rating_schema_url

    with urllib.request.urlopen(url + name) as resp:
        rr = resp.read()
        rj = json.loads(rr)
        # differentiate between errors, schema list,
        # and the requested schema response

        if "errors" in rj:
            raise Exception(rj)

        if "schemas" not in rj and "last-modified" in resp.headers:
            # pull last-modified information from the header
            lm = resp.headers["last-modified"]
            return rj, lm

        return rj["schemas"] if "schemas" in rj else rj


def supported(scac: str, ebol: bool = True) -> list:
    """
    Get the supported methods of the provided APIs to the specific carrier SCACs.

    Args:

        scac - scac of the carrier you would like to check
        ebol - True-ish if you want to check ebol_21 methods
            False-ish if you want to check pickup methods

    Returns a list of methods supported by the API, like:

        ["POST", ...]

    """
    api = "ebol_21" if ebol else "pickup"
    params = {"scac": scac, "api": api}
    with urllib.request.Request(
        supported_url + urllib.parse.urlencode(params)
    ) as resp:
        return json.loads(resp.read())


def supported_pretty(scac: str, ebol: bool = True) -> list:
    """
    Get the supported methods of the provided APIs to the specific carrier SCACs,
    returning the full names of the supported API methods.

    Args:

        scac - scac of the carrier you would like to check
        ebol - True-ish if you want to check ebol_21 methods
            False-ish if you want to check pickup methods

    Returns a list of methods supported by the API, like:

        ["<scac>.ebol.post", ...]

    """
    which = "ebol" if ebol else "pickup"
    pfx = f"{scac}.{which}.".lower()

    return [pfx + m.lower() for m in supported(scac, ebol)]
