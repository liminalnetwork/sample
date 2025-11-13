# module src.shared

## src.shared [src/shared.py](src/shared.py)

This module includes functions shared by other portions of this client
implementation.

## Builtin modules

[json](https://docs.python.org/3/library/json.html)  
[urllib](https://docs.python.org/3/library/urllib.html)

## Classes defined here

* [settings](src.shared.md#settings)

### class <a name="settings">settings</a>(builtins.object)

overridden by `doc_client` when `doc_client` imports this module

---

Data descriptors defined here:

    __dict__
        dictionary for instance variables
    __weakref__
        list of weak references to the object

## Functions defined here

### <a name="-get_api_key">get_api_key</a>(scac\_or\_carrier\_id: str) -&gt; str

Args:

    scac_or_carrier_id - will use the mapping defined on
        settings.CARRIER_TO_CONFIG to discover the proper API key to use.

Returns:

    "...api key..."

### <a name="-get_schema">get_schema</a>(name: str = 'list') -&gt; Union[tuple, list]

Args:

    name - {scac}.{api}.{http method}

Returns:

    If the name provided is "list", will return:
        [name, name, ...]


    If name was previously returned by get_schema(), or was listed:
    https://account.liminalnetwork.com/account/carriers-schemas
    Will return:
        (json_schema, last_modified)

### <a name="-supported">supported</a>(scac: str, ebol: bool = True) -&gt; list

Get the supported methods of the provided APIs to the specific carrier SCACs.

Args:

    scac - scac of the carrier you would like to check
    ebol - True-ish if you want to check ebol_21 methods
        False-ish if you want to check pickup methods

Returns a list of methods supported by the API, like:

    ["POST", ...]

### <a name="-supported_pretty">supported_pretty</a>(scac: str, ebol: bool = True) -&gt; list

Get the supported methods of the provided APIs to the specific carrier SCACs,
returning the full names of the supported API methods.

Args:

    scac - scac of the carrier you would like to check
    ebol - True-ish if you want to check ebol_21 methods
        False-ish if you want to check pickup methods

Returns a list of methods supported by the API, like:

    ["<scac&gt;.ebol.post", ...]

## Data

ebol_url = 'https://api.liminalnetwork.com/{scac}/ebol_21'

pickup_url = 'https://api.liminalnetwork.com/{scac}/pickup'

schema_url = 'https://api.liminalnetwork.com/schema?name='

supported_url = 'https://api.liminalnetwork.com/supported?'

url = 'https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}'
