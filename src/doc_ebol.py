# Copyright 2025 Liminal Network
# See LICENSE for details

import json
import urllib.request
import urllib.parse

__doc__ = """
There are 3 functions defined here:

ebol_CU() - create or update an eBOL (not all carriers support updates)
ebol_get() - get an existing eBOL (not all carriers support get)
ebol_delete() - delete an existing eBOL (not all carriers support delete)

For more information about which carriers are supported, you can visit:
https://account.liminalnetwork.com/account/carriers-docs

All carrier schemas and last modified date can be found:
https://account.liminalnetwork.com/account/carriers-schemas

"""


from .shared import (
    get_schema,
    supported_pretty as supported,
    get_api_key,
    ebol_url,
)

# --- Electronic Bill of Lading eBOL Create, Update, Get, and Delete examples (POST, PUT, GET, DELETE)


def ebol_CU(
    scac: str,
    data: dict,
    verify_schema: bool = False,
    params: dict = None,
    create: bool = True,
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
            returned by get_schema(f'{scac}.ebol.{post for create, put for not create}')
        params - additional query parameters, can include:
            ignore_unprocessed=1/t/y
            debug_upstream=1/t/y
            istest=1/t/y
            raw=1/t/y
        create - if True-ish, will make a POST request to create an EBOL
            if False-ish, will make a PUT request to update an EBOL (not all
            carriers support updates)
        schema_override - if a string, will validate the `data` dictionary
            against this explicitly named schema (necessary when using a
            numeric scac)
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

    Sometimes, Liminal Network has chosen to modfiy the output of the Carrier's
    response; typically to include a `scac` entry, but sometimes to `normalize`
    error messages into an `"errors": [...]` entry in the root of the response,
    etc. If `params` includes a key named `raw` (along with additional query
    parameters you would like to include in your request to Liminal Network),
    Liminal Network will return the raw Carrier result, without modifications.

    Example:

        # if the contents of src/doc_*.py and src/shared.py are in your path as "ln":

        from ln.doc_client import ebol_CU, settings
        settings.LIMINAL_NETWORK_API_KEY = ...

        ebol_response = ebol_CU(
            scac,
            ebol_data,
            True,  # go ahead and verify
        )

    """
    method = "post" if create else "put"
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

        schema, _ = get_schema(schema_override or f"{scac}.ebol.{method}")
        # returns nothing onsuccess, raises exception on failure
        jsonschema.validate(schema=schema, instance=data)

    elif check_supported:
        supp = supported(scac, True)
        schema = schema_override or f"{scac}.ebol.{method}"
        if schema.lower() not in supp:
            raise ValueError(f"{schema} not supported")

    url = ebol_url.format(scac=scac)
    nparams = dict(params)
    nparams["auth"] = get_api_key(scac)
    url += "?" + urllib.parse.urlencode(nparams)

    headers = {
        "Content-Type": "application/json",
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode(),
        headers=headers,
        method=method.upper(),
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


def ebol_get(
    scac: str,
    check_supported: bool = False,
    **params: dict,
):
    """
    Fetch an eBOL
    Note: not all carrier APIs provide eBOL GET, check via `supported(scac)`

    Args:

        scac - scac or carrier_id you are trying to make an ebol get against
        check_supported - if True-ish, will verify the API exists by calling
            supported() with the appropriate arguments
        **params - data representing the relevant tracking number for fetching
            eBOLs for the specific carrier.
            debug_upstream=1/t/y
            istest=1/t/y
            raw=1/t/y

    If no carrier-supported named tracking value is provided as part of `**params`,
    making the call will return the tracking parameters supported.

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

        from ln.doc_client import ebol_get, settings
        settings.LIMINAL_NETWORK_API_KEY = ...

        ebol_data = ebol_get(
            scac,
            bol=...
        )
    """
    if check_supported:
        supp = supported(scac, True)
        schema = f"{scac}.ebol.get".lower()
        if schema not in supp:
            raise ValueError(f"{schema} not supported")

    url = ebol_url.format(scac=scac)
    nparams = dict(params)
    nparams["auth"] = get_api_key(scac)
    url += "?" + urllib.parse.urlencode(nparams)

    with urllib.request.urlopen(urllib.request.Request(url)) as resp:
        text = resp.read()
        if resp.headers.get("content-type") == "application/json":
            return json.loads(text)
        # some upstreams return XML if raw or debug_upstream, so return the text unchagned
        return text


def ebol_delete(
    scac: str,
    check_supported: bool = False,
    **params: dict,
):
    """
    Delete an eBOL
    Note: not all carrier APIs provide eBOL DELETE, check via `supported(scac)`

    Args:

        scac - scac or carrier_id you are trying to make an ebol delete against
        **params - data representing the relevant tracking number for fetching
            eBOLs for the specific carrier.
            debug_upstream=1/t/y
            istest=1/t/y
            raw=1/t/y

    If no carrier-supported named tracking value is provided as part of `**params`,
    making the call will return the tracking parameters supported.

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

        from ln.doc_client import ebol_delete, settings
        settings.LIMINAL_NETWORK_API_KEY = ...

        ebol_delete_confirmation = ebol_delete(
            scac,
            bol=...
        )
    """
    if check_supported:
        supp = supported(scac, True)
        schema = f"{scac}.ebol.delete".lower()
        if schema not in supp:
            raise ValueError(f"{schema} not supported")

    url = ebol_url.format(scac=scac)
    nparams = dict(params)
    nparams["auth"] = get_api_key(scac)
    url += "?" + urllib.parse.urlencode(nparams)

    with urllib.request.urlopen(
        urllib.request.Request(url), method="DELETE"
    ) as resp:
        text = resp.read()
        if resp.headers.get("content-type") == "application/json":
            return json.loads(text)
        # some upstreams return XML if raw or debug_upstream, so return the text unchagned
        return text
