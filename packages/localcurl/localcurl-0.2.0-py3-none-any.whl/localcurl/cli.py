from __future__ import annotations

import argparse
import shlex
import sys
from typing import Any, Callable, Protocol, TextIO

import pyperclip
import requests
from requests.models import PreparedRequest, Response

from . import parsers
from . import request_adapters


class ClipboardInterface(Protocol):
    def paste(self) -> str: ...


class SessionLike(Protocol):
    verify: bool | str | None

    def __enter__(self) -> SessionLike: ...
    def __exit__(self, *args: Any) -> None: ...
    def send(self, request: PreparedRequest) -> Response: ...


def main(
    cmd_line_args: list[str] = sys.argv,
    stdin: TextIO = sys.stdin,
    clipboard: ClipboardInterface = pyperclip,
    session_factory: Callable[[], SessionLike] = requests.Session,
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "local_addr",
        metavar="addrport",
        help="The local address to send the request, e.g. http://localhost:8080",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--keep-host-cookie-prefix",
        action="store_true",
        help="Prevent stripping __Host- prefix from cookies",
    )
    parser.add_argument(
        "curl_command",
        nargs=argparse.REMAINDER,
        help="The curl command to parse (reads from stdin if not provided)",
    )
    args = parser.parse_args(args=cmd_line_args[1:])

    if args.curl_command:
        curl_command = shlex.join(args.curl_command)
    else:
        # No curl command was provided as arguments, try to read from stdin or the
        # clipboard.
        curl_command = clipboard.paste() if stdin.isatty() else stdin.read()

    # If the curl command has was split across multiple lines (with trailing
    # backslashes) it ends having "\\\n" characters in it that would cause the curl
    # command parser to fail. We need to remove them.
    curl_command = curl_command.replace("\\\n", "")
    curl_command = curl_command.replace("\\\r\n", "")

    try:
        request = parsers.curl_to_request(curl_command)
    except parsers.CurlParsingError as e:
        print(f"Unrecognized curl command: {e}", file=sys.stderr)
        return 1

    # Transform the request to use the local address
    request_adapters.replace_url_address(request, args.local_addr)
    request_adapters.replace_header_addresses(request, args.local_addr)

    # Strip the __Host- prefix from cookies unless instructed otherwise.
    if args.keep_host_cookie_prefix is False:
        request_adapters.strip_host_cookie_prefix(request)

    with session_factory() as session:
        session.verify = not args.no_verify
        response = session.send(request.prepare())

    if _is_binary_response(response):
        # For binary data, write directly to stdout buffer without newlines
        sys.stdout.buffer.write(response.content)
        sys.stdout.buffer.flush()
    else:
        sys.stdout.write(response.text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


_COMMON_TEXT_TYPES = [
    'text/',
    'application/json',
    'application/xml',
    'application/javascript',
    'application/x-javascript',
    'application/ecmascript',
    'application/x-www-form-urlencoded',
    'application/xhtml+xml',
    'application/rss+xml',
    'application/atom+xml',
    'application/soap+xml',
    'application/hal+json',
    'application/ld+json',
    'application/x-yaml',
    'application/yaml',
]

def _is_binary_response(response: Response) -> bool:
    """Determine if a response contains binary data based on Content-Type header. """
    content_type = response.headers.get('Content-Type', '').lower()

    if any(content_type.startswith(text_type) for text_type in _COMMON_TEXT_TYPES):
        return False

    # Try to decode as text as a fallback
    try:
        response.content.decode('utf-8')
        return False
    except UnicodeDecodeError:
        return True
