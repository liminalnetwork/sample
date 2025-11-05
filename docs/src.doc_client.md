# module src.doc_client

## [src.md](src).doc_client [/app/src/doc_client.py](/app/src/doc_client.py)

Names available in this module are imported from:
    shared
    doc_visibility
    doc_presigned
    doc_webhook_handler
    doc_ebol
    doc_pickup


If you would like to use this library directly, rather than rewriting or
copying/pasting, you should:

1. import doc_client
2.
  a. overwrite attributes on doc_client.[settings](#settings)  
     OR
  b. import shared; replace shared.[settings](#settings) with your custom [object](builtins.md#object)
3. use one or more of the imported methods in doc_client, or the other relevant doc_*.py modules

## Builtin modules

[json](https://docs.python.org/3/library/json.html)  
[os](https://docs.python.org/3/library/os.html)  
[sqlite3](https://docs.python.org/3/library/sqlite3.html)<br />

## Imported modules

[src.shared](src.shared.md)

## Classes

* [builtins.object](builtins.md#object)
  * [settings](src.doc_client.md#settings) ([builtins.object](builtins.md#object))

class <a name="settings">*settings*</a>(builtins.object)

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
to the CARRIER_TO_CONFIG mapping.

Data descriptors defined here:

    *__dict__*
        dictionary for instance variables
    *__weakref__*
        list of weak references to the object

Data and other attributes defined here:

    *CARRIER_TO_CONFIG* = {'': 'LIMINAL_NETWORK_API_KEY', 'LN': 'LIMINAL_NET...
    *KNOWN_SANDBOX_KEY* = 'qNAJFePYEfzZag1pDqv'
    *LIMINAL_NETWORK_API_KEY* = 'qNAJFePYEfzZag1pDqv'
    *LIMINAL_NETWORK_FINAL_MILE_API_KEY* = 'qNAJFePYEfzZag1pDqv'

## Functions defined here

### <a name="-main">main</a>()

## Imported functions

[src.doc_ebol](src.doc_ebol.md)
> [ebol_CU()](src.doc_ebol.md#-ebol_CU)
> [ebol_delete()](src.doc_ebol.md#-ebol_delete)
> [ebol_get()](src.doc_ebol.md#-ebol_get)

[src.doc_pickup](src.doc_pickup.md)
> [pickup_CU()](src.doc_pickup.md#-pickup_CU)
> [pickup_delete()](src.doc_pickup.md#-pickup_delete)
> [pickup_get()](src.doc_pickup.md#-pickup_get)

[src.doc_presigned](src.doc_presigned.md)
> [limited_use_key()](src.doc_presigned.md#-limited_use_key)

[src.doc_visibility](src.doc_visibility.md)
> [cancel_hook()](src.doc_visibility.md#-cancel_hook)
> [get_hook_status()](src.doc_visibility.md#-get_hook_status)
> [get_individual_images()](src.doc_visibility.md#-get_individual_images)
> [get_pdf_images()](src.doc_visibility.md#-get_pdf_images)
> [get_status()](src.doc_visibility.md#-get_status)
> [register_hook()](src.doc_visibility.md#-register_hook)

[src.doc_webhook_handler](src.doc_webhook_handler.md)
> [get_all_to_db()](src.doc_webhook_handler.md#-get_all_to_db)
> [get_images_to_db()](src.doc_webhook_handler.md#-get_images_to_db)
> [get_status_to_db()](src.doc_webhook_handler.md#-get_status_to_db)
> [handle_end()](src.doc_webhook_handler.md#-handle_end)
> [handle_image()](src.doc_webhook_handler.md#-handle_image)
> [handle_request()](src.doc_webhook_handler.md#-handle_request)
> [handle_start()](src.doc_webhook_handler.md#-handle_start)
> [handle_status()](src.doc_webhook_handler.md#-handle_status)
> [insert_data()](src.doc_webhook_handler.md#-insert_data)
> [setup_schema()](src.doc_webhook_handler.md#-setup_schema)

[src.shared](src.shared.md)
> [get_api_key()](src.shared.md#-get_api_key)
> [get_schema()](src.shared.md#-get_schema)
> [supported()](src.shared.md#-supported)
