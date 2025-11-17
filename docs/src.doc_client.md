# module src.doc_client

## src.doc_client [src/doc_client.py](../src/doc_client.py)

Names available in this module are imported from:

    shared
    doc_visibility
    doc_presigned
    doc_webhook_handler
    doc_ebol
    doc_pickup


If you would like to use this library directly, rather than rewriting or
copying/pasting, you should:

1. `import doc_client`
2. Pick ONE of:
   1. overwrite attributes on doc_client.[settings](#settings) OR
   2. after `import doc_client`, `import shared` and replace shared.[settings](#settings) with your custom [object](builtins.md#object)
3. use one or more of the imported methods in `doc_client`, or the other relevant `doc_\*.py` modules

## Imported modules

[src.shared](src.shared.md)

## Builtin modules

[json](https://docs.python.org/3/library/json.html)
[os](https://docs.python.org/3/library/os.html)
[sqlite3](https://docs.python.org/3/library/sqlite3.html)

## Classes defined here

* [settings](src.doc_client.md#settings)

### class <a name="settings">settings</a>(builtins.object)

This basic settings object overwrites shared.settings when you import this
module. This settings object has a default config that will allow you to
make requests against our sandbox API for the functions:

    get_status()
    get_pdf_images()
    get_individual_images()
    register_hook()
    cancel_hook()
    get_hook_status()
    limited_use_key()

For single-API key uses, you can likely overwrite the attributes
`LIMINAL_NETWORK_API_KEY` and `LIMINAL_NETWORK_FINAL_MILE_API_KEY` as
necessary. For different API keys per scac or carrier id, you would
want to add attributes to this object, then add the scac or carrier id
to the `CARRIER_TO_CONFIG` mapping.

---

Data descriptors defined here:

    __dict__
        dictionary for instance variables
    __weakref__
        list of weak references to the object

---

Data and other attributes defined here:

    CARRIER_TO_CONFIG = {'': 'LIMINAL_NETWORK_API_KEY', 'LN': 'LIMINAL_NET...
    KNOWN_SANDBOX_KEY = 'qNAJFePYEfzZag1pDqv'
    LIMINAL_NETWORK_API_KEY = 'qNAJFePYEfzZag1pDqv'
    LIMINAL_NETWORK_FINAL_MILE_API_KEY = 'qNAJFePYEfzZag1pDqv'

## Functions defined here

### <a name="-main">main</a>()

This [main](#-main)() function provides a command-line interface to the
visibility API. Try running via "python3 -m src.doc_client --help"
for live usage information.

    usage: python3 -m src.doc_client [-h] [--verbose] [--creds CREDS]
                                    (--database | --files | --sign SIGN |
                                    --webhook WEBHOOK | --email EMAIL)
                                    [--sqlite-file SQLITE_FILE]
                                    [--dirname DIRNAME] [--scac SCAC]
                                    [--count COUNT] [--duration DURATION]
                                    [--status STATUS] [--dispatch DISPATCH]
                                    [pro ...]

    positional arguments:
    pro                   The tracking number, pro, or reference number for your
                            shipment (ignored when --sign=rating)

    options:
    -h, --help            show this help message and exit
    --verbose             Provide to receive additional output
    --creds CREDS         The 'package.module.attribute' to use for your API Key
    --database            Provide to store in a local sqlite db, see --sqlite-
                            file for name
    --files               Provide to store in individual .jpg and .json files,
                            see --dirname for alternate destination directories
    --sign SIGN           call /sign with the comma-separated list of methods to
                            allow: date,status,lading,proof,rating (see also:
                            --count and --duration)
    --webhook WEBHOOK     call the /webhook endpoint and register the provided
                            url
    --email EMAIL         call the /webhook endpoint and register the provided
                            email address
    --sqlite-file SQLITE_FILE
                            Sqlite database to store our data to
    --dirname DIRNAME     Where to store downloaded files
    --scac SCAC           The scac or carrier_id of the carrier to contact
    --count COUNT         how many times to allow calls with the api key
                            returned from /sign (1-100 valid)
    --duration DURATION   how long to allow calls with the api key returned from
                            /sign (1 to 2592000 seconds)
    --status STATUS       which statuses to report to the web / email hook, or
                            'all' to get all updates
    --dispatch DISPATCH   The filename of the json-encoded file with
                            [request_body, is_base64_encoded, is_json] stored
                            inside for dispatching via handle_request() (requires
                            --database)

## Imported functions

From **[src.doc_ebol](src.doc_ebol.md)** [src/doc_ebol.py](../src/doc_ebol.py)
* [ebol_CU()](src.doc_ebol.md#-ebol_CU)
* [ebol_delete()](src.doc_ebol.md#-ebol_delete)
* [ebol_get()](src.doc_ebol.md#-ebol_get)

From **[src.doc_pickup](src.doc_pickup.md)** [src/doc_pickup.py](../src/doc_pickup.py)
* [pickup_CU()](src.doc_pickup.md#-pickup_CU)
* [pickup_delete()](src.doc_pickup.md#-pickup_delete)
* [pickup_get()](src.doc_pickup.md#-pickup_get)

From **[src.doc_presigned](src.doc_presigned.md)** [src/doc_presigned.py](../src/doc_presigned.py)
* [limited_use_key()](src.doc_presigned.md#-limited_use_key)

From **[src.doc_visibility](src.doc_visibility.md)** [src/doc_visibility.py](../src/doc_visibility.py)
* [cancel_hook()](src.doc_visibility.md#-cancel_hook)
* [get_hook_status()](src.doc_visibility.md#-get_hook_status)
* [get_individual_images()](src.doc_visibility.md#-get_individual_images)
* [get_pdf_images()](src.doc_visibility.md#-get_pdf_images)
* [get_status()](src.doc_visibility.md#-get_status)
* [register_hook()](src.doc_visibility.md#-register_hook)

From **[src.doc_webhook_handler](src.doc_webhook_handler.md)** [src/doc_webhook_handler.py](../src/doc_webhook_handler.py)
* [get_all_to_db()](src.doc_webhook_handler.md#-get_all_to_db)
* [get_images_to_db()](src.doc_webhook_handler.md#-get_images_to_db)
* [get_status_to_db()](src.doc_webhook_handler.md#-get_status_to_db)
* [handle_end()](src.doc_webhook_handler.md#-handle_end)
* [handle_image()](src.doc_webhook_handler.md#-handle_image)
* [handle_request()](src.doc_webhook_handler.md#-handle_request)
* [handle_start()](src.doc_webhook_handler.md#-handle_start)
* [handle_status()](src.doc_webhook_handler.md#-handle_status)
* [insert_data()](src.doc_webhook_handler.md#-insert_data)
* [setup_schema()](src.doc_webhook_handler.md#-setup_schema)

From **[src.shared](src.shared.md)** [src/shared.py](../src/shared.py)
* [get_api_key()](src.shared.md#-get_api_key)
* [get_schema()](src.shared.md#-get_schema)
* [supported()](src.shared.md#-supported)
