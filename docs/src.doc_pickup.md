# module src.doc_pickup

## [src.md](src).doc_pickup [/app/src/doc_pickup.py](/app/src/doc_pickup.py)

There are 3 functions defined here:

    [pickup_CU](#-pickup_CU)() - create or update a pickup (not all carriers support updates)
    [pickup_get](#-pickup_get)() - get an existing pickup request (not all carriers support get)
    [pickup_delete](#-pickup_delete)() - delete an existing pickup request (not all carriers support delete)

For more information about which carriers are supported, you can visit:
[https://account.liminalnetwork.com/account/carriers-docs](https://account.liminalnetwork.com/account/carriers-docs)

All carrier schemas and last modified date can be found:
[https://account.liminalnetwork.com/account/carriers-schemas](https://account.liminalnetwork.com/account/carriers-schemas)

## Functions defined here

### <a name="-pickup_CU">pickup_CU</a>(<br />    scac: str,<br />    data: dict,<br />    verify_schema: bool = False,<br />    params: dict = None,<br />    create: bool = True,<br />    schema_override: str = '',<br />    want_headers: bool = False,<br />    check_supported: bool = False<br />)

Create or Update a Pickup request
Note: not all carrier APIs provide Pickup Update (PUT), check via `supported(scac, False)`

Args:

    scac - scac or carrier_id you are trying to make an pickup post/put against
    data - dict representing the request, whose contents follow the format
        defined by the relevant JSON schema (&lt;scac&gt;.pickup.&lt;post or put&gt;)
    verify_schema - if True, will validate &lt;data&gt; against the schema
        returned by get_schema(f'{scac}.pickup.&lt;post for create, put for not create&gt;')
    params - additional query parameters, can include:
        ignore_unprocessed=1/t/y
        debug_upstream=1/t/y
        istest=1/t/y
        raw=1/t/y
    create - if True-ish, will make a POST request to create a pickup request
        if False-ish, will make a PUT request to update a pickup request (not all
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

### <a name="-pickup_delete">pickup_delete</a>(scac: str, check_supported: bool = False, **params: dict)

Delete a Pickup request
Note: not all carrier APIs provide Pickup DELETE, check via `supported(scac)`

Args:

    scac - scac or carrier_id you are trying to make an pickup delete against
    check_supported - if True-ish, will verify the API exists by calling
        `supported()` with the appropriate arguments
    **params - data representing the relevant tracking number for fetching
        pickup requests for the specific carrier.
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

### <a name="-pickup_get">pickup_get</a>(scac: str, check_supported: bool = False, **params: dict)

Fetch a Pickup request
Note: not all carrier APIs provide Pickup GET, check via `supported(scac)`

Args:

    scac - scac or carrier_id you are trying to make an ebol get against
    check_supported - if True-ish, will verify the API exists by calling
        `supported()` with the appropriate arguments
    **params - data representing the relevant tracking number for fetching
        Pickup requests for the specific carrier.
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

*pickup_url* = 'https://api.liminalnetwork.com/{scac}/pickup'
