# doc_client module documentation

Please see [LiminalNetwork.com](https://www.liminalnetwork.com) for more details.

## Configuration

### *class* doc_client.settings

Bases: `object`:

    CARRIER_TO_CONFIG = {'': 'LIMINAL_NETWORK_API_KEY', 'LN': 'LIMINAL_NETWORK_FINAL_MILE_API_KEY', 'SANDBOX': 'KNOWN_SANDBOX_KEY'}
    KNOWN_SANDBOX_KEY = 'qNAJFePYEfzZag1pDqv'
    LIMINAL_NETWORK_API_KEY = 'qNAJFePYEfzZag1pDqv'
    LIMINAL_NETWORK_FINAL_MILE_API_KEY = 'qNAJFePYEfzZag1pDqv'

This class should be replaced with a secure credential store of some kind,
along with `get_api_key()` as applicable for your needs.


### doc_client.get_api_key(scac_or_carrier_id)

The implementation is shorter than the description:

    if scac_or_carrier_id in settings.CARRIER_TO_CONFIG:
        return getattr(settings, settings.CARRIER_TO_CONFIG[scac_or_carrier_id])
    return getattr(settings, settings.CARRIER_TO_CONFIG[""])


## Liminal Network API interface


### doc_client.get_status(pro: str, scac_or_carrier_id: str | int = 'LN') → dict

Args:

  pro - the tracking number or pro of the shipment you would like information about
  scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
    the string “LN”, or the carrier_id shown on the Carrier Credentials page;
    defaults to “LN” for Liminal Network Final Mile Photos service

Returns one of:

    {
      : “errors”: […]
    }
    OR
    {
      ‘delivery_date’: ‘…’,
      ‘delivery_time’: ‘…’,
      ‘status’: ‘…’,
      ‘longstatus’: ‘…’,
      ‘scac’: ‘…’,
      ‘pro’: ‘…’
    }


### doc_client.get_pdf_images(pro: str, which: str, scac_or_carrier_id: str | int = 'LN', test_output: bool = False)

Args:

    pro - shipment identifier
    which - one of “lading” or “proof”
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
      LN, or the carrier_id shown on the Carrier Credentials page;
      defaults to “LN” for Liminal Network Final Mile Photos service
    test_output - if true, check the content of the output to verify that
      it is probably a PDF

Fetches the images for the given PRO from Liminal Network as a PDF,
saving to “{pro}_{which}.pdf” on the local filesystem.

Returns:
Error message returned by server on non-2xx response as dictionary  
OR  
Filename of pdf stored for 2xx responses as string


### doc_client.get_individual_images(pro: str, which: str, indexes: tuple = (), scac_or_carrier_id: str | int = 'LN', test_output: bool = False)

Args:

    pro - shipment identifier
    which - one of “lading” or “proof”
    indexes - tuple or general iterable of indexes of images to fetch,
      containing integer values 0 to 10, inclusive.
      Default: (1,2,3,4,5,6,7,8,9,10)
      Image 0 is the “header” image from the pdf, 1 is the first real
      image.
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
      LN, or the carrier_id shown on the Carrier Credentials page;
      defaults to “LN” for Liminal Network Final Mile Photos service
    test_output - if true, check the content of the each output file to
      verify that it is probably a jpeg image

Fetches the images for the given PRO from Liminal Network as jpegs,
saving to “{pro}_{which}_{number}.jpg” on the local filesystem for any
images fetched.

Returns:
    List of image filenames stored on the local disk.

## Webhook / Email hook interface

### doc_client.register_hook(scac: str, url_or_email: str, status: str, pro: str = '', bol: str = '', tracking: str = '') → str | dict

Args:

    scac - SCAC or carrier_id of the intended carrier
    url_or_email - [user@yourdomain.com](mailto:user@yourdomain.com) OR http(s)://[[sub.]sub.]yourdomain.com/…
    status - can be any status expected from the carrier, which will be the one
      status sent. If you want all changes in status, provide the string “all”.
    pro - use one of pro, bol, or tracking
    bol - use one of pro, bol, or tracking
    tracking - use one of pro, bol, or tracking

Will call Liminal Network’s webhook registry API for the scac/shipment pair provided provided.

On success, returns:

    webhook_id

On failure, returns:

    {“errors”: […]}

### doc_client.get_hook_status(webhook_id: str) → dict

Args:

    webhook_id - a webhook_id returned by register_hook() that is still valid

Returns:

dictionary containing your status, or an error indicating that the webhook is invalid

### doc_client.cancel_hook(webhook_id: str) → dict

Args:

    webhook_id - a webhook_id returned by register_hook() that is still valid

Returns:

confirmation that your webhook was deleted, or an error indicating that the
webhook is invalid (was already deleted, or it never existed)


## /sign interface for use in emails and embedded webpages


### doc_client.limited_use_key(carrier: str | int, methods: list | tuple | set | str = 'status', count: int = 1, duration: int = 300, pro: str = None, bol: str = None, tracking: str = None) → str | dict

Args:

    carrier - numeric id of the carrier, as found from the /tracking page
    methods - sequence of strings, or comma-separated string of API methods
      to allow access to. Defaults to status, can include:
      status,date,lading,proof,rating
    count - number of times this can be accessed, 1 to 100, default 1
    duration - how long should this key be valid, 1 to 2592000
      1 second to 1 month, default 300 = 5 minutes
    pro - pick one of pro, bol, or tracking, and provide your number
    bol - pick one of pro, bol, or tracking, and provide your number
    tracking - pick one of pro, bol, or tracking, and provide your number

On success, returns:

    "Auth Key As string"

On failure, returns:

    {“errors”: […]}




## SQlite3 databse interface


### doc_client.setup_schema(conn)

Args:

    conn - sqlite or other db connection with .execute() and .commit()

Applies embedded ddl to the given conn.

Note: syntax is valid SQLite3, unknown compatibility with other databases.


### doc_client.insert_data(conn, table: str, data: dict)

Args:

    conn - sqlite or other db connection with .execute() and .commit()
    table - what table to insert into
    data - data to insert into the database table

Inserts data into the provided table, committing the results when done.
Uses ‘?’ for argument wildcards, may be compatible with other database
client libraries.


### doc_client.get_status_to_db(conn, pro: str, scac_or_carrier_id: str | int = 'LN') → dict

Args:

    conn - sqlite3 connection object
    pro - pro to get images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
      LN, or the carrier_id shown on the Carrier Credentials page;
      defaults to “LN” for Liminal Network Final Mile Photos service

Inserts the status metadata for the given pro into the database specified,
into the table named known_shipments. On error will not change the DB.

Returns:

    get_status() call results for testing / verification

### doc_client.get_images_to_db(conn, pro: str, scac_or_carrier_id: str | int = 'LN')

Args:

    conn - sqlite3 connection object
    pro - pro to get images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
      LN, or the carrier_id shown on the Carrier Credentials page;
      defaults to “LN” for Liminal Network Final Mile Photos service

Inserts all images for the given pro into the database specified,
into the table named shipment_images.

### doc_client.get_all_to_db(conn, pro: str, scac_or_carrier_id: str | int = 'LN')

Args:

    conn - sqlite3 connection object
    pro - pro to get status and images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
      LN, or the carrier_id shown on the Carrier Credentials page;
      defaults to “LN” for Liminal Network Final Mile Photos service

Will call get_status_to_db(), and if the status is one to expect images,
will subsequently call get_images_to_db().

### doc_client.handle_request(conn, request_body: str | bytes, body_base64_encoded: bool, body_json_encoded: bool) → str

Args:

    conn - database connection
    request_body - the body of the http(s) request
    body_base64_encoded - true if the body was base64 encoded, and must be decoded
    body_json_encoded - true if the body was json encoded, otherwise was x-www-form-urlencoded

Handles “start”, “status”, “image”, and “end” webhook requests, inserting their results into
our demonstration sqlite db.

On success, returns:

    “ok“

On failure, returns:

    “error-...“

### doc_client.handle_start(conn, now: str, ref: str)

Args:

    conn - database connection
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

Ensures that ref is represented in known_shipments. If not,
will add the row with status of QR_SCANNED.

### doc_client.handle_status(conn, post_data: dict, now: str, ref: str)

Args:

    conn - database connection
    post_data - {“name”: [“val”], …}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

Ensures that ref is represented in known_shipments. If not,
will add the row with status reported by the webhook call.


### doc_client.handle_image(conn, post_data: dict, now: str, ref: str) → str

Args:

    conn - database connection
    post_data - {“name”: [“val”], …}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

If “ok” is returned, will have processed and inserted the image in the post
data to the database.

On success, returns:

    “ok“

On failure, returns:

    “error-...“

### doc_client.handle_end(conn, post_data: dict, now: str, ref: str) → str

Args:

    conn - database connection
    post_data - {“name”: [“val”], …}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

If “ok” is returned, will have updated the status of the provided
shipment to whatever was provided in the post_data.

## command-line interface

### doc_client.main()

Run via:

    $ python3 doc_client.py --help
