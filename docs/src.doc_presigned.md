# module src.doc_presigned

## src.doc_presigned [/app/src/doc_presigned.py](/app/src/doc_presigned.py)

This module defines one function:

    [limited_use_key](#-limited_use_key)()

This allows you to "sign" a request, returning a "temporary" API key, which
can then be used to fetch information about a given shipment without needing
your API key. This is primarily used for embedding images in web pages, and
creating transactional email links:

    key = [limited_use_key](#-limited_use_key)(
        scac,
        ["status", "proof", "lading", "image"],
        count=10, \# caller can use this api key 10 times
        duration=7\*86400 \# the api key will last up to 1 week,
        pro=...
    )

    if isinstance(key, str):
        \# this link can be used in a transactional email, allowing for users
        \# to fetch the image without knowing your API key
        url = f"[https://api.liminalnetwork.com/{scac}/proof?api\_key={key](https://api.liminalnetwork.com/{scac}/proof?api\_key={key)}"
    else:
        raise Exception(key["errors])

## Builtin modules

[json](https://docs.python.org/3/library/json.html)  
[urllib](https://docs.python.org/3/library/urllib.html)

## Functions defined here

### <a name="-limited_use_key">limited_use_key</a>(<br />    carrier: Union[str, int],<br />    methods: Union[list, tuple, set, str] = 'status',<br />    count: int = 1,<br />    duration: int = 300,<br />    pro: str = None,<br />    bol: str = None,<br />    tracking: str = None<br />) -&gt; Union[str, dict]

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

## Imported functions

From **[src.shared](src.shared.md)** [src/shared.py](src/shared.py)
* [get_api_key()](src.shared.md#-get_api_key)

## Data

url = 'https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}'
