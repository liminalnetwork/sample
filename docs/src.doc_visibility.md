# module src.doc_visibility

## [src.md](src).doc_visibility [/app/src/doc_visibility.py](/app/src/doc_visibility.py)

This module defines functions for Liminal Network's Visibility API package:

    [get_status](#-get_status)()
    [get_pdf_images](#-get_pdf_images)()
    [get_individual_images](#-get_individual_images)()
    [register_hook](#-register_hook)()
    [get_hook_status](#-get_hook_status)()
    [cancel_hook](#-cancel_hook)()

The functions `[get_status](#-get_status)()`, `[get_pdf_images](#-get_pdf_images)()`, and `[get_individual_images](#-get_individual_images)()`
directly return information about a given shipment, while `[register_hook](#-register_hook)()`,
`[get_hook_status](#-get_hook_status)()`, and `[cancel_hook](#-cancel_hook)()` provide access to our webhook interface
for automatically reporting status information upstream to your provided webhook
or email address.

## Functions defined here

### <a name="-cancel_hook">cancel_hook</a>(webhook_id: str) -&gt; dict

Args:

    webhook_id - a webhook_id returned by [register_hook](#-register_hook)() that is still valid

Returns:

    confirmation that your webhook was deleted, or an error indicating that the
    webhook is invalid (was already deleted, or it never existed)

### <a name="-get_hook_status">get_hook_status</a>(webhook_id: str) -&gt; dict

Args:

    webhook_id - a webhook_id returned by [register_hook](#-register_hook)() that is still valid

Returns:

    dictionary containing your status, or an error indicating that the webhook is invalid

### <a name="-get_individual_images">get_individual_images</a>(<br />    pro: str,<br />    which: str,<br />    indexes: tuple = (),<br />    scac_or_carrier_id: Union[str, int] = 'LN',<br />    test_output: bool = False<br />)

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
saving to "&lt;pro&gt;_&lt;which&gt;_&lt;number&gt;.jpg" on the local filesystem for any
images fetched.

Returns:

    List of image filenames stored on the local disk.

### <a name="-get_pdf_images">get_pdf_images</a>(<br />    pro: str,<br />    which: str,<br />    scac_or_carrier_id: Union[str, int] = 'LN',<br />    test_output: bool = False<br />)

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

### <a name="-get_status">get_status</a>(pro: str, scac_or_carrier_id: Union[str, int] = 'LN') -&gt; dict

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

### <a name="-register_hook">register_hook</a>(<br />    scac: str,<br />    url_or_email: str,<br />    status: str,<br />    pro: str = '',<br />    bol: str = '',<br />    tracking: str = ''<br />) -&gt; Union[str, dict]

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

## Data

*url* = 'https://api.liminalnetwork.com/{scac}/{method}?auth={api_key}&pro={pro}'
