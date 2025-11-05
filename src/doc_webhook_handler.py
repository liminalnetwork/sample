# Copyright 2025 Liminal Network
# See LICENSE for details

import base64
import datetime
import os
from typing import Union
import urllib.parse

from .doc_visibility import get_status, get_individual_images

__docs__ = """
This module defines functions for most of a sample webhook handler, which
can take requests from Liminal Network's webhook reporting, and insert them
into a local database.

This includes the Database setup function:

    setup_schema()

A simple database insert function:

    insert_data()

Three functions for explicitly fetching data from the visibility API:

    get_status_to_db()
    get_images_to_db()
    get_all_to_db()

And five functions for processing and handling incoming webhook requests:

    handle_request() - processes an entire request, decoding data
    handle_start() - processes "start delivery" webhook
    handle_status() - processes "status update" webhook
    handle_image() - processes image webhook
    handle_end() - processes "end delivery" webhook
"""


# --- take web -> disk output and insert into sqlite database


def setup_schema(conn):
    """
    Args:
        conn - sqlite or other db connection with .execute() and .commit()

    Applies embedded ddl to the given conn.

    Note: syntax is valid SQLite3, unknown compatibility with other databases.
    """
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS known_shipments(
            pro TEXT UNIQUE ON CONFLICT REPLACE,
            status TEXT,
            longstatus TEXT,
            delivery_time TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS shipment_images(
            known_pro TEXT REFERENCES known_shipments(pro) ON DELETE CASCADE,
            image_identifier TEXT,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            image_data BLOB,
            UNIQUE (known_pro, image_identifier)
                ON CONFLICT REPLACE
        );
        """,
    ]
    for d_i in ddl:
        conn.execute(d_i)
        conn.commit()


def insert_data(conn, table: str, data: dict):
    """
    Args:
        conn - sqlite or other db connection with .execute() and .commit()
        table - what table to insert into
        data - data to insert into the database table

    Inserts data into the provided table, committing the results when done.
    Uses '?' for argument wildcards, may be compatible with other database
    client libraries.
    """
    if "scac" in data:
        # prefix our stored pros with the SCAC
        data = dict(data)
        prefix = data.pop("scac")
        data["pro"] = f'{prefix}-{data["pro"]}'
    cols = list(data)
    columns = ",".join(cols)
    vals = ",".join(len(cols) * ["?"])
    query = f"INSERT INTO {table}({columns}) VALUES ({vals});" ""
    conn.execute(query, [data[k] for k in cols])
    conn.commit()


def get_status_to_db(
    conn, pro: str, scac_or_carrier_id: Union[str, int] = "LN"
) -> dict:
    """
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
    """
    status = get_status(pro, scac_or_carrier_id)
    if "errors" in status:
        return status
    to_insert = {
        k: status[k] for k in ("pro", "status", "longstatus", "delivery_time")
    }
    to_insert["pro"] = str(scac_or_carrier_id) + "-" + to_insert["pro"]
    insert_data(conn, "known_shipments", to_insert)
    return status


def get_images_to_db(
    conn, pro: str, scac_or_carrier_id: Union[str, int] = "LN"
):
    """
    Args:
        conn - sqlite3 connection object
        pro - pro to get images for
        scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
            LN, or the carrier_id shown on the Carrier Credentials page;
            defaults to "LN" for Liminal Network Final Mile Photos service

    Inserts all images for the given pro into the database specified,
    into the table named shipment_images.
    """
    identifier = f"{scac_or_carrier_id}-{pro}"
    for image_name in get_individual_images(
        pro, "proof", (), scac_or_carrier_id
    ):
        try:
            with open(image_name, "rb") as img:
                # If you wanted to use an object store instead,
                # change this code.
                img_data = img.read()
                to_insert = {
                    "known_pro": identifier,
                    "image_identifier": image_name,
                    "image_data": img_data,
                }
                insert_data(conn, "shipment_images", to_insert)
        except FileNotFoundError:
            print(image_name, os.getcwd(), os.listdir("."))
            raise

        # remember to delete the local temporary file
        os.unlink(image_name)


def get_all_to_db(conn, pro: str, scac_or_carrier_id: Union[str, int] = "LN"):
    """
    Args:
        conn - sqlite3 connection object
        pro - pro to get status and images for
        scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
            LN, or the carrier_id shown on the Carrier Credentials page;
            defaults to "LN" for Liminal Network Final Mile Photos service

    Will call get_status_to_db(), and if the status is one to expect images,
    will subsequently call get_images_to_db().
    """
    status = get_status_to_db(conn, pro, scac_or_carrier_id)
    if "errors" not in status:
        # can try to get any uploaded images any time there isn't an error
        get_images_to_db(conn, pro, scac_or_carrier_id)


# --- handle webhook requests generically


def handle_request(
    conn,
    request_body: Union[str, bytes],
    body_base64_encoded: bool,
    body_json_encoded: bool,
) -> str:
    """
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

    """
    # decode the post body
    if body_base64_encoded:
        request_body = base64.b64decode(
            request_body
            if isinstance(request_body, bytes)
            else request_body.encode("latin-1")
        )

    body = (
        request_body
        if isinstance(request_body, str)
        else request_body.decode("latin-1")
    )

    # parse the post body
    if body_json_encoded:
        # for compat with parse_qs()
        post_data = {k: [v] for k, v in json.loads(body).items()}
    else:
        post_data = urllib.parse.parse_qs(body)

    for it in ("ref", "what"):
        if not post_data.get(it):
            return f"error-{it}"

    ref = post_data.get("ref")[0]
    what = post_data.get("what")[0]
    now_dt = datetime.datetime.now(datetime.timezone.utc)
    now = now_dt.replace(microsecond=0, tzinfo=None).isoformat()
    now += "+0000"

    # dispatch
    if what == "start":
        handle_start(conn, now, ref)
        return "ok"

    if what == "status":
        handle_status(conn, post_data, now, ref)
        return "ok"

    if what == "image":
        return handle_image(conn, post_data, now, ref)

    if what == "end":
        return handle_end(conn, post_data, now, ref)

    return "error-unknown-" + what


def handle_start(conn, now: str, ref: str):
    """
    Args:

        conn - database connection
        now - utcnow string
        ref - pro, tracking, or reference number for the shipment

    Ensures that ref is represented in known_shipments. If not,
    will add the row with status of QR_SCANNED.
    """
    exist_query = "SELECT pro FROM known_shipments WHERE pro = ?"
    if list(conn.execute(exist_query, [ref])):
        # don't re-insert
        return

    insert_data(
        conn,
        "known_shipments",
        {
            "pro": ref,
            "status": "QR_SCANNED",
            "longstatus": "QR Code was scanned",
            "delivery_time": now,
        },
    )


def handle_status(conn, post_data: dict, now: str, ref: str):
    """
    Args:

        conn - database connection
        post_data - {"name": ["val"], ...}
        now - utcnow string
        ref - pro, tracking, or reference number for the shipment

    Ensures that ref is represented in known_shipments. If not,
    will add the row with status reported by the webhook call.
    """
    insert_data(
        conn,
        "known_shipments",
        {
            "pro": ref,
            "status": post_data["status"][0],
            "longstatus": post_data["longstatus"][0],
            "delivery_time": post_data["delivery_date"][0],
        },
    )


def handle_image(conn, post_data: dict, now: str, ref: str) -> str:
    """
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

    """
    for it in ("filename", "image"):
        if not post_data.get(it):
            return f"error-{it}"

    image = post_data["image"][0]
    if not image.startswith("data:"):
        return "error-image-data"

    # "data:image/jpeg;base64,"

    try:
        if ";base64," in image[:25]:
            image_bytes = base64.b64decode(image.partition(",")[-1].encode())
    except Exception:
        # POST body should support at least up to 418,000 bytes to
        # receive image data. If your platform encodes base64 as handled
        # by handle_request(), then you should ensure your post data limit
        # is at least 558,000 bytes.
        return "error-image-data"

    # ensure foreign key exists
    handle_start(conn, now, ref)

    # will be <pro>_<image_type>.jpg, which matches the filenames returned
    # by get_individual_images()
    filename = post_data["filename"][0]

    insert_data(
        conn,
        "shipment_images",
        {
            "known_pro": ref,
            "image_identifier": filename,
            "image_data": image_bytes,
        },
    )
    return "ok"


def handle_end(conn, post_data: dict, now: str, ref: str) -> str:
    """
    Args:

        conn - database connection
        post_data - {"name": ["val"], ...}
        now - utcnow string
        ref - pro, tracking, or reference number for the shipment

    If "ok" is returned, will have updated the status of the provided
    shipment to whatever was provided in the post_data.

    Returns one of:

        "ok"
        "error-<what was the problem>"
    """
    if not post_data.get("longstatus"):
        return "error-longstatus"

    # this matches what is returned by get_status()
    status, _, longstatus = post_data.get("longstatus")[0].partition(" - ")

    # ensure the row exists
    handle_start(conn, now, ref)

    # update the row
    conn.execute(
        """
        UPDATE known_shipments
        SET status = ?, longstatus = ?
        WHERE pro = ?
    """,
        [status, longstatus, ref],
    )
    conn.commit()
    return "ok"
