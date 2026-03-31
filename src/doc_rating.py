# Copyright 2026 Liminal Network
# See LICENSE for details

import json
from typing import Union
import urllib.request
import urllib.parse

__doc__ = """
There are 3 functions defined here:

rating() - make a rating request
prepare_address() - prepares address information for rating()
prepare_freight() - prepares freight information for rating()

For more information about which carriers are supported, you can visit:
https://account.liminalnetwork.com/account/carriers-docs

All carrier schemas and last modified date can be found:
https://account.liminalnetwork.com/account/carriers-schemas

"""


from .shared import (
    get_schema,
    supported_pretty as supported,
    get_api_key,
    rating_url,
)


# --- /rating POST request


def rating(
    scac: str,
    data: dict,
    verify_schema: bool = False,
    params: dict = None,
    schema_override: str = "",
    want_headers: bool = False,
    check_supported: bool = False,
):
    """
    Create or Update an eBOL
    Note: not all carrier APIs provide eBOL Update (PUT), check via `supported(scac)`

    Args:

        scac - scac or carrier_id you are trying to make an ebol post/put against
        data - dict representing the request, whose contents follow the format
            defined by the relevant JSON schema ({scac}.ebol.{post or put})
        verify_schema - if True, will validate {data} against the schema
            returned by get_schema('{scac}.ebol.{post for create, put for not create}')
        schema_override - if a string, will validate the `data` dictionary
            against this explicitly named schema (necessary when using a
            numeric scac)
        params - additional query parameters, can include:
            debug_upstream=1/t/y
            istest=1/t/y
            raw=1/t/y
        want_headers - if True-ish, will return (response, headers_dict)
            if False-ish, will return response
        check_supported - if verify_schema is False-ish, and check_supported
            is True-ish, will verify that the API exists and is supported
            first by calling supported() with the appropriate arguments

    If `verify_schema` is true-ish, we will make a request to get_schema() to get
    the relevant schema, then verify data using jsonschema (a 3rd party module).
    If no errors are found during schema validation, we will make a post request
    to Liminal Network with default credentials, returning the results of your
    request.

    If `verify_schema` is false-ish, and `check_supported` is true-ish then will
    call supported with appropriate arguments, to make sure the API exists before
    we call it.

    If `ignore_unprocessed` is `1/t/y`, Liminal Network will ignore any fields that
    are unprocessed, but provided by the caller, which are normally reported as
    errors to you, before calling the carrier's API.

    If `debug_upstream` is `1/t/y`, and there are no upstream validation errors,
    Liminal Network will return the request that Liminal Network would have sent
    to the carrier's API.

    If `istest` is `1/t/y`, and `debug_upstream` is not one of `1/t/y`, Liminal Network
    will return either a pre-canned upstream test response, or if the upstream
    API has their own explicit test/QA environment, will ensure the test/QA
    environment is used, and return the response from the carrier.

    Sometimes, Liminal Network chooses to modfiy the output of the Carrier's
    response. If `params` includes a key named `raw` (along with additional query
    parameters you would like to include in your request to Liminal Network),
    Liminal Network will return the raw Carrier result, without modifications
    (but will include authentication response headers if want_headers is provided
    and true-ish).

    Example:

        # if the contents of src/doc_*.py and src/shared.py are in your path as "ln/*":

        from ln.doc_client import rating, settings
        settings.LIMINAL_NETWORK_API_KEY = ...

        # To get the schema:
        # from ln.shared import get_schema
        # get_schema(f"{scac}.rating.post")

        rating_response = rating(
            scac,
            pickup_data,
        )

    """
    scac = scac.lower()
    if verify_schema:
        if scac.isdigit() and not schema_override:
            raise Exception(
                "we cannot auto-verify a schema with a numeric scac, please include a schema_override value with a schema name <scac>.ebol.<post or put>"
            )

        try:
            import jsonschema
        except ImportError:
            raise Exception(
                "please install jsonschema to enable client side schema verification"
            )

        schema = get_schema(schema_override or f"{scac}.rating.post")
        if not isinstance(schema, dict):
            raise Exception(f"Invalid upstream schema response: {args}")

        # returns nothing onsuccess, raises exception on failure
        jsonschema.validate(schema=schema, instance=data)

    elif check_supported:
        schema = schema_override or f"{scac}.rating.post"
        sch = get_schema(schema)
        if not isinstance(sch, dict):
            raise ValueError(f"{schema} not supported")

    url = rating_url.format(scac=scac)
    nparams = dict(params)
    nparams["auth"] = get_api_key(scac)
    url += "?" + urllib.parse.urlencode(nparams)

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers=headers,
        method="POST",
    )

    with urllib.request.urlopen(req) as resp:
        text = resp.read()

        if resp.headers.get("content-type") == "application/json":
            ret = json.loads(text)
        else:
            # some upstreams return XML if raw or debug_upstream, so return the text unchagned
            ret = text

        if want_headers:
            return ret, dict(resp.headers)

        return ret


# --- Helper functions


def prepare_address(
    city: str,
    state: str,
    zip: str,
    country: str = "",
    name: str = "",
    name_plus: str = "",
    addr: str = "",
    acct: str = "",
) -> str:
    """
    Args:
        city - address city
        state - address state
        zip - address postal code
        country - address country
        name - company name
        name_plus - contact at company
        addr - street address of location
        acct - account number associated with this address

    Some carriers may not require country, name, name_plus, and acct on all
    address or location fields.

    Example:

        origin = prepare_address(city, state, zip, country)

    """
    return urllib.parse.urlencode(
        ",".join(
            [city, state, zip, country, name, name_plus, addr, acct]
        ).rstrip(",")
    )


def prepare_freight(
    length: int,
    width: int,
    height: int,
    weight: int,
    frt_class: str,
    count: Union[str, int] = "",
    type: str = "",
    nmfc_item: str = "",
    nmfc_sub: str = "",
):
    """
    Args:
        length - length of item in Inches
        width - width of item in Inches
        height - height of item in Inches
        weight - weight of item in Pounds
        frt_class - class of item
        count - number of items of this type (usually defaults to 1 upstream
            if not provided), can also represent count:pieces or units:pieces
            for some carriers
        type - item to be picked up: bag, box, plt, ... (usually defaults to plt
            upstream if not provided)
        nmfc_item - NMFC Item freight class
        nmfc_sub - NMFC Item freight subclass

    Not all carriers require NMFC item and sub information, but callers should
    provide valid dimension, weight, freight class, count, and type information.

    Example:

        # This is for 2x 500 pound pallets of class 50, with the provided nmfc classes
        # it is 48" long, 40" wide, and 48" tall. Claims to be class 50 (most carriers
        # will correct freight classes if they are incorrect)

        frt1 = prepare_freight(48, 40, 48, 500, "50", 2, "PLT", "115030", "02")

    """
    return urllib.parse.urlencode(
        ",".join(map(str, [x for x in items if x not in (None, "")]))
    )
