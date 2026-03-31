# module src.doc_rating

## src.doc_rating [src/doc_rating.py](../src/doc_rating.py)

There are 3 functions defined here:

[rating](#-rating)() - make a rating request  
[prepare_address](#-prepare_address)() - prepares address information for [rating](#-rating)()  
[prepare_freight](#-prepare_freight)() - prepares freight information for [rating](#-rating)()  

For more information about which carriers are supported, you can visit:
[https://account.liminalnetwork.com/account/carriers-docs](https://account.liminalnetwork.com/account/carriers-docs)

All carrier schemas and last modified date can be found:
[https://account.liminalnetwork.com/account/carriers-schemas](https://account.liminalnetwork.com/account/carriers-schemas)

## Builtin modules

[json](https://docs.python.org/3/library/json.html)  
[urllib](https://docs.python.org/3/library/urllib.html)

## Functions defined here

### <a name="-prepare_address">prepare_address</a>(<br />    city: str,<br />    state: str,<br />    zip: str,<br />    country: str = '',<br />    name: str = '',<br />    name\_plus: str = '',<br />    addr: str = '',<br />    acct: str = ''<br />) -&gt; str

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

### <a name="-prepare_freight">prepare_freight</a>(<br />    length: int,<br />    width: int,<br />    height: int,<br />    weight: int,<br />    frt\_class: str,<br />    count: Union[str, int] = '',<br />    type: str = '',<br />    nmfc\_item: str = '',<br />    nmfc\_sub: str = ''<br />)

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

### <a name="-rating">rating</a>(<br />    scac: str,<br />    data: dict,<br />    verify\_schema: bool = False,<br />    params: dict = None,<br />    schema\_override: str = '',<br />    want\_headers: bool = False,<br />    check\_supported: bool = False<br />)

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

    # if the contents of src/doc_\*.py and src/shared.py are in your path as "ln/\*":

    from ln.doc_client import rating, settings
    settings.LIMINAL_NETWORK_API_KEY = ...

    # To get the schema:
    # from ln.shared import get_schema
    # get_schema(f"{scac}.rating.post")

    rating_response = rating(
        scac,
        pickup_data,
    )

## Imported functions

From **[src.shared](src.shared.md)** [src/shared.py](../src/shared.py)
* [get_api_key()](src.shared.md#-get_api_key)
* [get_schema()](src.shared.md#-get_schema)
* [supported()](src.shared.md#-supported)

## Data

rating_url = 'https://api.liminalnetwork.com/{scac}/rating'
