# module src.doc_presigned

## src.doc_presigned [src/doc_presigned.py](../src/doc_presigned.py)

This module defines one function:

    limited_use_key()

This allows you to "sign" a request, returning a "temporary" API key, which
can then be used to fetch information about a given shipment without needing
your API key. This is primarily used for embedding images in web pages, and
creating transactional email links:

    key = limited_use_key(
        scac,
        ["status", "proof", "lading", "image"],
        count=10, \# caller can use this api key 10 times
        duration=7\*86400 # the api key will last up to 1 week,
        pro=...
    )

    if isinstance(key, str):
        # this link can be used in a transactional email, allowing for users
        # to fetch the image without knowing your API key
        url = f"https://api.liminalnetwork.com/{scac}/proof?auth={key}"
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

Example:

    # if the contents of src/doc_\*.py and src/shared.py are in your path as "ln":

    from ln.doc_client import get_status, settings
    settings.LIMINAL_NETWORK_API_KEY = ...

    # when you receive a proof of delivery image via webhook or otherwise,
    # you can generate a key so that you can send an email with an image link
    # to the user, and / or display the image directly on your webpage in an
    # iframe or img tag, without worrying about leaking your real API key

    key = limited_use_key(scac, "proof", 10, 7\*86400, pro=pro)
    url = f"https://api.liminalnetwork.com/{scac}/proof?auth={key}"

## Imported functions

From **[src.shared](src.shared.md)** [src/shared.py](../src/shared.py)
* [get_api_key()](src.shared.md#-get_api_key)

## Data

url = 'https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}'
