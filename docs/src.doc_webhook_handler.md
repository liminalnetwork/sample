# module src.doc_webhook_handler

## src.doc_webhook_handler [src/doc_webhook_handler.py](src/doc_webhook_handler.py)

\# Copyright 2025 Liminal Network
\# See LICENSE for details

## Builtin modules

[base64](https://docs.python.org/3/library/base64.html)  
[datetime](https://docs.python.org/3/library/datetime.html)  
[os](https://docs.python.org/3/library/os.html)  
[urllib](https://docs.python.org/3/library/urllib.html)

## Functions defined here

### <a name="-get_all_to_db">get_all_to_db</a>(conn, pro: str, scac\_or\_carrier\_id: Union[str, int] = 'LN')

Args:
    conn - sqlite3 connection object
    pro - pro to get status and images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
        LN, or the carrier_id shown on the Carrier Credentials page;
        defaults to "LN" for Liminal Network Final Mile Photos service

Will call [get_status_to_db](#-get_status_to_db)(), and if the status is one to expect images,
will subsequently call [get_images_to_db](#-get_images_to_db)().

### <a name="-get_images_to_db">get_images_to_db</a>(conn, pro: str, scac\_or\_carrier\_id: Union[str, int] = 'LN')

Args:
    conn - sqlite3 connection object
    pro - pro to get images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
        LN, or the carrier_id shown on the Carrier Credentials page;
        defaults to "LN" for Liminal Network Final Mile Photos service

Inserts all images for the given pro into the database specified,
into the table named shipment_images.

### <a name="-get_status_to_db">get_status_to_db</a>(conn, pro: str, scac\_or\_carrier\_id: Union[str, int] = 'LN') -&gt; dict

Args:
    conn - sqlite3 connection object
    pro - pro to get images for
    scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
        LN, or the carrier_id shown on the Carrier Credentials page;
        defaults to "LN" for Liminal Network Final Mile Photos service

Inserts the status metadata for the given pro into the database specified,
into the table named known_shipments. On error will not change the DB.

Returns:
    get_status() call results for testing / verification

### <a name="-handle_end">handle_end</a>(conn, post\_data: dict, now: str, ref: str) -&gt; str

Args:

    conn - database connection
    post_data - {"name": ["val"], ...}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

If "ok" is returned, will have updated the status of the provided
shipment to whatever was provided in the post_data.

Returns one of:

    "ok"
    "error-&lt;what was the problem&gt;"

### <a name="-handle_image">handle_image</a>(conn, post\_data: dict, now: str, ref: str) -&gt; str

Args:

    conn - database connection
    post_data - {"name": ["val"], ...}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

If "ok" is returned, will have processed and inserted the image in the post
data to the database.

On success, returns:

    "ok"

On failure, returns:

    "error-..."

### <a name="-handle_request">handle_request</a>(<br />    conn,<br />    request\_body: Union[str, bytes],<br />    body\_base64\_encoded: bool,<br />    body\_json\_encoded: bool<br />) -&gt; str

Args:

    conn - database connection
    request_body - the body of the http(s) request
    body_base64_encoded - true if the body was base64 encoded, and must be decoded
    body_json_encoded - true if the body was json encoded, otherwise was x-www-form-urlencoded

Handles "start", "status", "image", and "end" webhook requests, inserting their results into
our demonstration sqlite db.

On success, returns:

    "ok"

On failure, returns:

    "error-..."

### <a name="-handle_start">handle_start</a>(conn, now: str, ref: str)

Args:

    conn - database connection
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

Ensures that ref is represented in known_shipments. If not,
will add the row with status of QR_SCANNED.

### <a name="-handle_status">handle_status</a>(conn, post\_data: dict, now: str, ref: str)

Args:

    conn - database connection
    post_data - {"name": ["val"], ...}
    now - utcnow string
    ref - pro, tracking, or reference number for the shipment

Ensures that ref is represented in known_shipments. If not,
will add the row with status reported by the webhook call.

### <a name="-insert_data">insert_data</a>(conn, table: str, data: dict)

Args:
    conn - sqlite or other db connection with .execute() and .commit()
    table - what table to insert into
    data - data to insert into the database table

Inserts data into the provided table, committing the results when done.
Uses '?' for argument wildcards, may be compatible with other database
client libraries.

### <a name="-setup_schema">setup_schema</a>(conn)

Args:
    conn - sqlite or other db connection with .execute() and .commit()

Applies embedded ddl to the given conn.

Note: syntax is valid SQLite3, unknown compatibility with other databases.

## Imported functions

From **[src.doc_visibility](src.doc_visibility.md)** [src/doc_visibility.py](src/doc_visibility.py)
* [get_individual_images()](src.doc_visibility.md#-get_individual_images)
* [get_status()](src.doc_visibility.md#-get_status)

## Data

__docs__ = '\nThis module defines functions for most of a sam... handle_end() - processes "end delivery" webhook\n'
