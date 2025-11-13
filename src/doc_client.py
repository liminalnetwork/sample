# Copyright 2024 Liminal Network
# Released under the MIT license

# Example client, sqlite storage, and webhook handler implementations

__doc__ = """

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
   1. overwrite attributes on doc_client.settings OR
   2. after `import doc_client`, `import shared` and replace shared.settings with your custom object
3. use one or more of the imported methods in `doc_client`, or the other relevant `doc_*.py` modules

"""


import json  # for decoding some API reponses
import os  # to delete temporary files
import sqlite3  # replace with your database access method
from . import shared


# replace with your own secure credential store, and not the sandbox key
class settings:
    """
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

    """
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

# override settings in shared resources
shared.settings = settings

# import names
from .shared import get_api_key, get_schema, supported
from .doc_visibility import (
    get_status,
    get_pdf_images,
    get_individual_images,
    register_hook,
    cancel_hook,
    get_hook_status,
)
from .doc_presigned import limited_use_key
from .doc_webhook_handler import (
    setup_schema,
    insert_data,
    get_status_to_db,
    get_images_to_db,
    get_all_to_db,
    handle_request,
    handle_start,
    handle_status,
    handle_image,
    handle_end,
)

from .doc_ebol import ebol_CU, ebol_get, ebol_delete
from .doc_pickup import pickup_CU, pickup_get, pickup_delete


def main():
    """
    This main() function provides a command-line interface to the
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

    """
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
        help="Provide to store in individual .jpg and .json files, see --dirname for alternate destination directories",
    )
    group.add_argument(
        "--sign",
        default="",
        help="call /sign with the comma-separated list of methods to allow: date,status,lading,proof,rating (see also: --count and --duration)",
    )
    group.add_argument(
        "--webhook",
        default="",
        help="call the /webhook endpoint and register the provided url",
    )
    group.add_argument(
        "--email",
        default="",
        help="call the /webhook endpoint and register the provided email address",
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
        help="how many times to allow calls with the api key returned from /sign (1-100 valid)",
    )
    parser.add_argument(
        "--duration",
        default=300,
        type=int,
        help="how long to allow calls with the api key returned from /sign (1 to 2592000 seconds)",
    )
    parser.add_argument(
        "--status",
        default="",
        help="which statuses to report to the web / email hook, or 'all' to get all updates",
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
            print(
                limited_use_key(
                    args.scac,
                    sign,
                    args.count,
                    args.duration,
                    args.pro[0] if args.pro else "",
                )
            )
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
