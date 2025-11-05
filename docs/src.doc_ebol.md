# module src.doc_ebol

## [src.md](src).doc_ebol [/app/src/doc_ebol.py](/app/src/doc_ebol.py)

There are 3 functions defined here:

    [ebol_CU](#-ebol_CU)() - create or update an eBOL (not all carriers support updates)
    [ebol_get](#-ebol_get)() - get an existing eBOL (not all carriers support get)
    [ebol_delete](#-ebol_delete)() - delete an existing eBOL (not all carriers support delete)

For more information about which carriers are supported, you can visit:
[https://account.liminalnetwork.com/account/carriers-docs](https://account.liminalnetwork.com/account/carriers-docs)

All carrier schemas and last modified date can be found:
[https://account.liminalnetwork.com/account/carriers-schemas](https://account.liminalnetwork.com/account/carriers-schemas)

## Functions defined here

### <a name="-ebol_CU">ebol_CU</a>(<br />    scac: str,<br />    data: dict,<br />    verify_schema: bool = False,<br />    params: dict = None,<br />    create: bool = True,<br />    schema_override: str = '',<br />    want_headers: bool = False,<br />    check_supported: bool = False<br />)

Create or Update an eBOL
Note: not all carrier APIs provide eBOL Update (PUT), check via `supported(scac)`

Args:

    scac - scac or carrier_id you are trying to make an ebol post/put against
    data - dict representing the request, whose contents follow the format
        defined by the relevant JSON schema (&lt;scac&gt;.ebol.&lt;post or put&gt;)
    verify_schema - if True, will validate &lt;data&gt; against the schema
        returned by get_schema(f'{scac}.ebol.&lt;post for create, put for not create&gt;')
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
        first by calling `supported()` with the appropriate arguments

If verify_schema is true-ish, we will make a request to get_schema() to get
the relevant schema, then verify data using jsonschema (a 3rd party module).
If no errors are found during schema validation, we will make a post request
to Liminal Network with default credentials, returning the results of your
request.

If verify_schema is false-ish, and check_supported is true-ish then will
call supported with appropriate arguments, to make sure the API exists before
we call it.

If ignore_unprocessed is 1/t/y, Liminal Network will ignore any fields that
are unprocessed, but provided by the caller, which are normally reported as
errors to you, before calling the carrier's API.

If debug_upstream is 1/t/y, and there are no upstream validation errors,
Liminal Network will return the request that Liminal Network would have sent
to the carrier's API.

If istest=1/t/y, and debug_upstream is not one of 1/t/y, Liminal Network
will return either a pre-canned upstream test response, or if the upstream
API has their own explicit test/QA environment, will ensure the test/QA
environment is used, and return the response from the carrier.

Sometimes, Liminal Network has chosen to modfiy the output of the Carrier's
response; typically to include a "scac" entry, but sometimes to "normalize"
error messages into an "errors": [...] entry in the root of the response,
etc. If `params` includes a key named "raw" (along with additional query
parameters you would like to include in your request to Liminal Network),
Liminal Network will return the raw Carrier result, without modifications.

### <a name="-ebol_delete">ebol_delete</a>(scac: str, check_supported: bool = False, **params: dict)

Delete an eBOL
Note: not all carrier APIs provide eBOL DELETE, check via `supported(scac)`

Args:

    scac - scac or carrier_id you are trying to make an ebol delete against
    **params - data representing the relevant tracking number for fetching
        eBOLs for the specific carrier.
        debug_upstream=1/t/y
        istest=1/t/y
        raw=1/t/y

If no carrier-supported named tracking value is provided as part of **params,
making the call will return the tracking parameters supported.

If debug_upstream is 1/t/y, and there are no upstream validation errors,
Liminal Network will return the request that Liminal Network would have sent
to the carrier's API.

If istest=1/t/y, and debug_upstream is not one of 1/t/y, Liminal Network
will return either a pre-canned upstream test response, or if the upstream
API has their own explicit test/QA environment, will ensure the test/QA
environment is used, and return the response from the carrier.

Sometimes, Liminal Network has chosen to modfiy the output of the Carrier's
response; typically to include a "scac" entry, but sometimes to "normalize"
error messages into an "errors": [...] entry in the root of the response,
etc. If `params` includes a key named "raw" (along with additional query
parameters you would like to include in your request to Liminal Network),
Liminal Network will return the raw Carrier result, without modifications.

### <a name="-ebol_get">ebol_get</a>(scac: str, check_supported: bool = False, **params: dict)

Fetch an eBOL
Note: not all carrier APIs provide eBOL GET, check via `supported(scac)`

Args:

    scac - scac or carrier_id you are trying to make an ebol get against
    check_supported - if True-ish, will verify the API exists by calling
        `supported()` with the appropriate arguments
    **params - data representing the relevant tracking number for fetching
        eBOLs for the specific carrier.
        debug_upstream=1/t/y
        istest=1/t/y
        raw=1/t/y

If no carrier-supported named tracking value is provided as part of **params,
making the call will return the tracking parameters supported.

If debug_upstream is 1/t/y, and there are no upstream validation errors,
Liminal Network will return the request that Liminal Network would have sent
to the carrier's API.

If istest=1/t/y, and debug_upstream is not one of 1/t/y, Liminal Network
will return either a pre-canned upstream test response, or if the upstream
API has their own explicit test/QA environment, will ensure the test/QA
environment is used, and return the response from the carrier.

Sometimes, Liminal Network has chosen to modfiy the output of the Carrier's
response; typically to include a "scac" entry, but sometimes to "normalize"
error messages into an "errors": [...] entry in the root of the response,
etc. If `params` includes a key named "raw" (along with additional query
parameters you would like to include in your request to Liminal Network),
Liminal Network will return the raw Carrier result, without modifications.

## Imported functions

[src.shared](src.shared.md)
> [get_api_key()](src.shared.md#-get_api_key)
> [get_schema()](src.shared.md#-get_schema)
> [supported()](src.shared.md#-supported)

## Data

*ebol_url* = 'https://api.liminalnetwork.com/{scac}/ebol_21'
