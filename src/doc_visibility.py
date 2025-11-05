# Copyright 2025 Liminal Network
# See LICENSE for details

import json
from typing import Union
import urllib.request

from .shared import url

__doc__ = """
This module defines functions for Liminal Network's Visibility API package:

    get_status()
    get_pdf_images()
    get_individual_images()
    register_hook()
    get_hook_status()
    cancel_hook()

The functions `get_status()`, `get_pdf_images()`, and `get_individual_images()`
directly return information about a given shipment, while `register_hook()`,
`get_hook_status()`, and `cancel_hook()` provide access to our webhook interface
for automatically reporting status information upstream to your provided webhook
or email address.
"""


# --- Visibility API Examples


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
    saving to "{pro}_{which}.pdf" on the local filesystem.

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


# --- Webhook interface


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

    Will call Liminal Network's webhook registry API for the scac/shipment pair provided.

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
