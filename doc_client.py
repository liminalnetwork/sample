# Copyright 2024 Liminal Network
# Released under the MIT license

# Example client, sqlite storage, and webhook handler implementations

import base64  # parsing requests
import datetime  # sometimes we need to know what time it is
import json  # for decoding some API reponses
import os  # to delete temporary files
import sqlite3  # replace with your database access method
import urllib.parse  # parsing requests
import urllib.request  # can also use another 3rd party library
import urllib.error  # for images being done
from typing import Union  # for mypy complaints


# --- plain web interface to disk


# replace with your own secure credential store, and not the sandbox key
class settings:
    # Keep the known sandbox key for the warning message in the command line
    # interface. used when scac == "SANDBOX"
    KNOWN_SANDBOX_KEY = "qNAJFePYEfzZag1pDqv"
    # used when scac == LN
    LIMINAL_NETWORK_FINAL_MILE_API_KEY = "qNAJFePYEfzZag1pDqv"
    # else used when scac != LN
    LIMINAL_NETWORK_API_KEY = "qNAJFePYEfzZag1pDqv"

    CARRIER_TO_CONFIG = {
        "SANDBOX": "KNOWN_SANDBOX_KEY",
        "LN": "LIMINAL_NETWORK_FINAL_MILE_API_KEY",
        "": "LIMINAL_NETWORK_API_KEY",
    }


url = "https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}"


def get_api_key(scac_or_carrier_id):
    # LN gets LIMINAL_NETWORK_FINAL_MILE_API_KEY
    # SANDBOX gets KNOWN_SANDBOX_KEY
    # everything else gets LIMINAL_NETWORK_API_KEY
    if scac_or_carrier_id in settings.CARRIER_TO_CONFIG:
        return getattr(settings, settings.CARRIER_TO_CONFIG[scac_or_carrier_id])
    return getattr(settings, settings.CARRIER_TO_CONFIG[""])


def get_status(pro: str, scac_or_carrier_id: Union[str, int] = "LN") -> dict:
    """
    Args:
        pro - the tracking number or pro of the shipment you would like information about
        scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
            the string "LN", or the carrier_id shown on the Carrier Credentials page;
            defaults to "LN" for Liminal Network Final Mile Photos service

    Returns one of:
            {
                "errors": [...]
            }
        OR
            {
                'delivery_date': '...',
                'delivery_time': '...',
                'status': '...',
                'longstatus': '...',
                'scac': '...',
                'pro': '...'
            }
    """
    full_url = url.format(
        method="status",
        api_key=get_api_key(scac_or_carrier_id),
        pro=pro,
        scac=scac_or_carrier_id,
    )
    return json.loads(urllib.request.urlopen(full_url).read().decode())


def get_pdf_images(
    pro: str,
    which: str,
    scac_or_carrier_id: Union[str, int] = "LN",
    test_output: bool = False,
):
    """
    Args:
        pro - shipment identifier
        which - one of "lading" or "proof"
        scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
            LN, or the carrier_id shown on the Carrier Credentials page;
            defaults to "LN" for Liminal Network Final Mile Photos service
        test_output - if true, check the content of the output to verify that
            it is probably a PDF

    Fetches the images for the given PRO from Liminal Network as a PDF,
    saving to "<pro>_<which>.pdf" on the local filesystem.

    Returns:
        Error message returned by server on non-2xx response as dictionary
        Filename of pdf stored for 2xx responses as string
    """
    full_url = (
        url.format(
            method=which,
            api_key=get_api_key(scac_or_carrier_id),
            pro=pro,
            scac=scac_or_carrier_id,
        )  # providing dl=1 flag ensures we get content-disposition response header
        + "&dl=1"
    )

    with urllib.request.urlopen(full_url) as resp:
        rr = resp.read()
        filename_header = resp.headers["content-disposition"]

    if not filename_header:
        return json.loads(rr.decode())

    filename = filename_header.partition("=")[-1].strip('"')
    if test_output:
        assert filename.endswith(".pdf"), (
            "File should be a pdf, not a: " + filename.rpartition(".")[-1]
        )
        assert b"PDF" in rr[:4], "File does not seem to be a pdf"

    # should be <pro>.pdf
    with open(filename, "wb") as out:
        out.write(rr)

    return filename


def get_individual_images(
    pro: str,
    which: str,
    indexes: tuple = (),
    scac_or_carrier_id: Union[str, int] = "LN",
    test_output: bool = False,
):
    """
    Args:
        pro - shipment identifier
        which - one of "lading" or "proof"
        indexes - tuple or general iterable of indexes of images to fetch,
            containing integer values 0 to 10, inclusive.
            Default: (1,2,3,4,5,6,7,8,9,10)
            Image 0 is the "header" image from the pdf, 1 is the first real
            image.
        scac_or_carrier_id - which carrier to use, either a 4-letter SCAC,
            LN, or the carrier_id shown on the Carrier Credentials page;
            defaults to "LN" for Liminal Network Final Mile Photos service
        test_output - if true, check the content of the each output file to
            verify that it is probably a jpeg image

    Fetches the images for the given PRO from Liminal Network as jpegs,
    saving to "<pro>_<which>_<number>.jpg" on the local filesystem for any
    images fetched.

    Returns:
        List of image filenames stored on the local disk.
    """
    if not indexes:
        # up to 5 normal images, 5 issue images
        indexes = tuple(range(1, 11))

    partial_url = (
        url.format(
            method=which,
            api_key=get_api_key(scac_or_carrier_id),
            pro=pro,
            scac=scac_or_carrier_id,
        )  # providing dl=1 flag ensures we get content-disposition response header
        + "&dl=1"
    )
    written = []
    for i in indexes:
        with urllib.request.urlopen(partial_url + f"&image={i}") as resp:
            rr = resp.read()
            filename_header = resp.headers["content-disposition"]

        if not filename_header:
            # no more images
            break

        filename = filename_header.partition("=")[-1].strip('"')
        if test_output:
            expect = b"PNG" if filename.endswith(".png") else b"JFIF"
            typ = filename.rpartition(".")[-1]
            assert typ in ("png", "jpg"), f"Unexpected filetype: {typ}"
            assert (
                expect in rr[:8]
            ), f"{filename} does not have expected {typ} content"

        print("got a file from the api", filename, i)

        # image=0 will be <pro>.png
        # image=1+ will be <pro>_<image_type>.jpg
        with open(filename, "wb") as out:
            out.write(rr)

        written.append(filename)

    return written


def register_hook(
    scac: str,
    url_or_email: str,
    status: str,
    pro: str = "",
    bol: str = "",
    tracking: str = "",
) -> Union[str, dict]:
    """
    Args:
        scac - SCAC or carrier_id of the intended carrier
        url_or_email - user@yourdomain.com OR http(s)://[[sub.]sub.]yourdomain.com/...
        status - can be any status expected from the carrier, which will be the one
            status sent. If you want all changes in status, provide the string "all".
        pro - use one of pro, bol, or tracking
        bol - use one of pro, bol, or tracking
        tracking - use one of pro, bol, or tracking

    Will call Liminal Network's webhook registry API for the scac/shipment pair provided provided.

    On success, returns:
        webhook_id

    On failure, returns:
        {"errors": [...]}

    """
    assert pro or bol or tracking
    base = (
        url.format(
            scac=scac,
            method="webhook",
            pro=pro,
            api_key=get_api_key(scac),
        )
        + "&"
        + urllib.parse.urlencode({"status": status})
    )

    if "//" in url_or_email:
        base += "&" + urllib.parse.urlencode({"webhook": url_or_email})
    else:
        base += "&" + urllib.parse.urlencode({"email": url_or_email})

    # handle pro vs bol vs tracking
    if not pro:
        # one of the other two should be valid
        rep = ("bol=" + bol) if bol else ("tracking=" + tracking)
        base = base.replace("pro=", rep, 1)

    ret = json.loads(urllib.request.urlopen(base).read().decode())
    if "webhook_id" in ret:
        return ret["webhook_id"]

    return ret


def get_hook_status(webhook_id: str) -> dict:
    """
    Args:
        webhook_id - a webhook_id returned by register_hook() that is still valid

    Returns:
        dictionary containing your status, or an error indicating that the webhook is invalid
    """
    return json.loads(
        urllib.request.urlopen(f"https://api.liminalnetwork.com/{webhook_id}")
        .read()
        .decode()
    )


def cancel_hook(webhook_id: str) -> dict:
    """
    Args:
        webhook_id - a webhook_id returned by register_hook() that is still valid

    Returns:
        confirmation that your webhook was deleted, or an error indicating that the
        webhook is invalid (was already deleted, or it never existed)
    """
    return json.loads(
        urllib.request.urlopen(
            f"https://api.liminalnetwork.com/{webhook_id}/cancel"
        )
        .read()
        .decode()
    )


def limited_use_key(
    carrier: Union[str, int],
    methods: Union[list, tuple, set, str] = "status",
    count: int = 1,
    duration: int = 300,
    pro: str = None,
    bol: str = None,
    tracking: str = None,
) -> Union[str, dict]:
    """
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
    """
    if not isinstance(methods, str):
        methods = ",".join(methods)
    methods = methods.replace("&", "")
    base = url.format(
        scac=carrier,
        method="sign",
        pro=pro,
        api_key=get_api_key(carrier),
    ) + (f"&methods={methods}&count={count}&duration={duration}")
    # provide one of pro=, bol=, or tracking=

    if not pro:
        # one of the other two should be valid
        rep = ("bol=" + bol) if bol else ("tracking=" + tracking)
        base = base.replace("pro=", rep, 1)

    ret = json.loads(urllib.request.urlopen(base).read().decode())
    if "auth" in ret:
        return ret["auth"]

    # there was an error
    return ret


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

    Handles "start", "image", and "end" webhook requests, inserting their results into
    our demonstration sqlite db.
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
        return handle_status(conn, post_data, now, ref)

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

    Returns one of:
        "ok"
        "error-<what was the problem>"

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


def main():
    import argparse
    import tempfile

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--verbose",
        default=False,
        action="store_true",
        help="Provide to receive additional output",
    )
    parser.add_argument(
        "--creds",
        default=None,
        help="The 'package.module.attribute' to use for your API Key",
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--database",
        default=False,
        action="store_true",
        help="Provide to store in a local sqlite db, see --sqlite-file for name",
    )
    group.add_argument(
        "--files",
        default=False,
        action="store_true",
        help="Provide to store in individual .jpg and .json files, see --dirname for name",
    )
    group.add_argument(
        "--sign",
        default="",
        help="call /sign with the comma-separated list of methods to allow: date,status,lading,proof,rating (see also: --count and --duration)"
    )
    group.add_argument(
        "--webhook",
        default="",
        help="call the /webhook endpoint and register the provided url"
    )
    group.add_argument(
        "--email",
        default="",
        help="call the /webhook endpoint and register the provided email address"
    )
    parser.add_argument(
        "--sqlite-file",
        default="finalmile_test.sqlite3",
        help="Sqlite database to store our data to",
    )
    parser.add_argument(
        "--dirname",
        default=tempfile.gettempdir(),
        help="Where to store downloaded files",
    )
    parser.add_argument(
        "--scac",
        default="LN",
        help="The scac or carrier_id of the carrier to contact",
    )
    parser.add_argument(
        "--count",
        default=1,
        type=int,
        help="how many times to allow calls with the api key returned from /sign (1-100 valid)"
    )
    parser.add_argument(
        "--duration",
        default=300,
        type=int,
        help="how long to allow calls with the api key returned from /sign (1 to 2592000 seconds)"
    )
    parser.add_argument(
        "--status",
        default="",
        help="which statuses to report to the web / email hook, or 'all' to get all updates"
    )
    group2 = parser.add_mutually_exclusive_group(required=True)
    group2.add_argument(
        "--dispatch",
        help="The filename of the json-encoded file with [request_body, is_base64_encoded, is_json] stored inside for dispatching via handle_request() (requires --database)",
    )
    group2.add_argument(
        "pro",
        nargs="*",
        default=[],
        help="The tracking number, pro, or reference number for your shipment (ignored when --sign=rating)",
    )
    allowed = set("date,status,lading,proof,rating".split(","))

    args = parser.parse_args()

    if args.dispatch and not args.database:
        print("--dispatch requires --database")
        return exit(1)

    if args.sign:
        if args.dispatch:
            print("Can't use --sign and --dispatch together")
            return exit(1)
        if args.database:
            print("Can't use --sign and --database together")
            return exit(1)
        sign = set(args.sign.split(","))
        no_good = sign - allowed
        if no_good:
            print("Bad --sign arguments:", ",".join(sorted(no_good)))
            return exit(1)

    if args.webhook or args.email:
        if len(args.pro) < 1:
            print("Requires at least one pro")
            return exit(1)

        if not args.status:
            print("Requires a status to wait for, or 'all'")
            return exit(1)

    if not args.creds:
        if (
            args.verbose
            and settings.KNOWN_SANDBOX_KEY
            == settings.LIMINAL_NETWORK_FINAL_MILE_API_KEY
        ):
            print("Warning: using SANDBOX API Key")

    else:
        import importlib

        module, _, attribute = args.creds.rpartition(".")
        package = None
        if "." in module:
            package, _, module = module.rpartition(".")
        mod = importlib.import_module(module, package)
        settings.LIMINAL_NETWORK_FINAL_MILE_API_KEY = getattr(mod, attribute)
        if args.verbose:
            print("Used API Key from", args.creds)

    # output to files
    cwd = os.getcwd()
    try:
        os.chdir(args.dirname)
        if args.database:
            if args.verbose:
                print("Opening database and ensuring schema validity")
            sq_conn = sqlite3.Connection(args.sqlite_file)
            setup_schema(sq_conn)

        if args.dispatch:
            if args.verbose:
                print("Opening", args.dispatch, "for incoming request data")

            with open(args.dispatch, "r") as inp:
                body, is_base64, is_json = json.load(inp)
                if args.verbose:
                    inp.seek(0)
                    print("dispatching:", inp.read(60), "...")

            resp = handle_request(sq_conn, body, is_base64, is_json)
            print("Response to request data:", resp)
            sq_conn.close()
            return

        elif args.database:
            for pro in args.pro:
                if args.verbose:
                    print("Fetching", pro)
                get_all_to_db(sq_conn, pro, args.scac)

            sq_conn.close()
            return

        elif args.sign:
            print(limited_use_key(
                args.scac,
                sign,
                args.count,
                args.duration,
                args.pro[0] if args.pro else "",
            ))
            return

        elif args.webhook or args.email:
            for pro in args.pro:
                print(
                    register_hook(
                        args.scac,
                        args.webhook or args.email,
                        "any",
                        pro,
                    )
                )
            return

        for pro in args.pro:
            if args.verbose:
                print("Fetching", pro)
            status = get_status(pro, args.scac)
            if "error" not in status:
                with open(f"{pro}.json", "w") as out:
                    json.dump(status, out)

                get_individual_images(pro, "proof", (), args.scac)

            elif args.verbose:
                print("Shipment had error:", status)

    finally:
        os.chdir(cwd)


if __name__ == "__main__":
    main()
