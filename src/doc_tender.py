# Copyright 2025 Liminal Network
# See LICENSE for details

import json
import urllib.request
import urllib.parse

__doc__ = """
There is 1 function defined here:

tender() - Make a /tender call, which encompasses /ebol_21 and /pickup calls

For more information about which carriers are supported, you can visit:
https://account.liminalnetwork.com/account/carriers-docs

All carrier schemas and last modified date can be found:
https://account.liminalnetwork.com/account/carriers-schemas

"""


from .shared import (
    get_schema,
    supported_pretty as supported,
    get_api_key,
    tender_url,
)

# --- Tender call to allow for multi-step


def tender(
    scac: str,
    data: dict,
    verify_schema: bool = False,
    params: dict = None,
    schema_override: str = "",
    want_headers: bool = False,
):
    """
    Make a /tender call

    Args:

        scac - scac or carrier_id you are trying to make an ebol post/put against
        data - dict representing the request, whose contents follow the format
            defined by the relevant JSON schema ({scac}.tender.post)
        verify_schema - if True, will validate {data} against the schema
            returned by get_schema('{scac}.tender.post')
        params - additional query parameters, can include:
            ignore_unprocessed=1/t/y
            debug_upstream=1/t/y
            istest=1/t/y
            raw=1/t/y
        schema_override - if a string, will validate the `data` dictionary
            against this explicitly named schema (necessary when using a
            numeric scac)
        want_headers - if True-ish, will return (response, headers_dict)
            if False-ish, will return response

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

    Sometimes, Liminal Network has chosen to modfiy the output of the Carrier's
    response; typically to include a `scac` entry, but sometimes to `normalize`
    error messages into an `"errors": [...]` entry in the root of the response,
    etc. If `params` includes a key named `raw` (along with additional query
    parameters you would like to include in your request to Liminal Network),
    Liminal Network will return the raw Carrier result, without modifications.

    Example:

        # if the contents of src/doc_*.py and src/shared.py are in your path as "ln":

        from ln.doc_client import tender, settings
        settings.LIMINAL_NETWORK_API_KEY = ...

        tender_response = tender(
            scac,
            tender_data,
            True,  # go ahead and verify
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

        schema, _ = get_schema(schema_override or f"{scac}.tender.post")
        # returns nothing onsuccess, raises exception on failure
        jsonschema.validate(schema=schema, instance=data)

    url = tender_url.format(scac=scac)
    nparams = dict(params)
    nparams["auth"] = get_api_key(scac)
    print("params", nparams)
    url += "?" + urllib.parse.urlencode(nparams)

    headers = {
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
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
