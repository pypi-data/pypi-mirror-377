import io
import shlex

import pytest
import requests

from localcurl.cli import main, _is_binary_response


def generate_test_parameters(
    localaddr: str, curl_command: str, optional_args: list[str] | None = None
):
    """
    Generate test parameters for the main function, accounting for the 3 different ways
    the curl command can be passed to the program:
    - From the command line
    - From stdin
    - From the clipboard
    """
    if optional_args is None:
        optional_args = []

    return (
        pytest.param(
            ["localcurl", *optional_args, localaddr, *shlex.split(curl_command)],
            "",
            True,
            "",
            id="curl_from_command_line",
        ),
        pytest.param(
            ["localcurl", *optional_args, localaddr],
            curl_command,
            False,
            "",
            id="curl_from_stdin",
        ),
        pytest.param(
            ["localcurl", *optional_args, localaddr],
            "",
            True,
            curl_command,
            id="curl_from_clipboard",
        ),
    )


@pytest.mark.parametrize(
    ["cmd_line_args", "stdin_value", "is_stdin_a_tty", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/", curl_command="curl https://example.com"
    ),
)
def test_get_url(
    cmd_line_args,
    stdin_value,
    is_stdin_a_tty,
    clipboard_value,
    make_fake_stdin,
    make_fake_clipboard,
    fake_session,
):
    """Test the CLI interface for a simple GET request."""
    exit_code = main(
        cmd_line_args=cmd_line_args,
        stdin=make_fake_stdin(isatty=is_stdin_a_tty, initial_value=stdin_value),
        clipboard=make_fake_clipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0
    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert fake_session.sent_request.method == "GET"



@pytest.mark.parametrize(
    ["cmd_line_args", "stdin_value", "is_stdin_a_tty", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/",
        curl_command="curl -b '__Host-foo=abc123' -H 'Cookie: __Host-bar=def456' https://example.com",
    ),
)
def test_strip_host_cookie_prefix_by_default(
    cmd_line_args,
    stdin_value,
    is_stdin_a_tty,
    clipboard_value,
    make_fake_stdin,
    make_fake_clipboard,
    fake_session,
):
    """Test that __Host- prefix is stripped by default."""
    exit_code = main(
        cmd_line_args=cmd_line_args,
        stdin=make_fake_stdin(isatty=is_stdin_a_tty, initial_value=stdin_value),
        clipboard=make_fake_clipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0
    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert "foo" in fake_session.sent_request._cookies
    assert "bar" in fake_session.sent_request._cookies
    assert "__Host-foo" not in fake_session.sent_request._cookies
    assert "__Host-bar" not in fake_session.sent_request._cookies


@pytest.mark.parametrize(
    ["cmd_line_args", "stdin_value", "is_stdin_a_tty", "clipboard_value"],
    generate_test_parameters(
        localaddr="http://localhost:8080/",
        curl_command="curl -b '__Host-foo=abc123' -H 'Cookie: __Host-bar=def456' https://example.com",
        optional_args=["--keep-host-cookie-prefix"],
    ),
)
def test_keep_host_cookie_prefix(
    cmd_line_args,
    stdin_value,
    is_stdin_a_tty,
    clipboard_value,
    make_fake_stdin,
    make_fake_clipboard,
    fake_session,
):
    """Test that __Host- prefix is kept when --keep-host-cookie-prefix is passed."""
    exit_code = main(
        cmd_line_args=cmd_line_args,
        stdin=make_fake_stdin(isatty=is_stdin_a_tty, initial_value=stdin_value),
        clipboard=make_fake_clipboard(clipboard_value),
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0
    assert fake_session.sent_request.url == "http://localhost:8080/"
    assert "__Host-foo" in fake_session.sent_request._cookies
    assert "__Host-bar" in fake_session.sent_request._cookies


def test_handle_lines_curl_args_line_breaks_from_stdin(
    make_fake_stdin,
    make_fake_clipboard,
    fake_session,
):
    """Test that line breaks in curl command are handled correctly."""
    curl_command = (
        "curl 'https://example.com' \\\n -H 'Accept: application/json, text/plain, */*'"
    )
    stdin = make_fake_stdin(isatty=False, initial_value=curl_command)
    clipboard = make_fake_clipboard()

    exit_code = main(
        cmd_line_args=["localcurl", "http://localhost:8080/"],
        stdin=stdin,
        clipboard=clipboard,
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0


def test_handle_lines_curl_args_line_breaks_from_clipboard(
    make_fake_stdin,
    make_fake_clipboard,
    fake_session,
):
    """Test that line breaks in curl command are handled correctly."""
    curl_command = (
        "curl 'https://example.com' \\\n -H 'Accept: application/json, text/plain, */*'"
    )
    stdin = make_fake_stdin()
    clipboard = make_fake_clipboard(initial_value=curl_command)

    exit_code = main(
        cmd_line_args=["localcurl", "http://localhost:8080/"],
        stdin=stdin,
        clipboard=clipboard,
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0


class FakeStdin(io.StringIO):
    """Mimics sys.stdin for testing purposes."""

    def __init__(
        self,
        isatty: bool = True,
        initial_value: str | None = "",
        newline: str | None = "\n",
    ):
        super().__init__(initial_value, newline)
        self._isatty = isatty

    def isatty(self):
        return self._isatty


@pytest.fixture
def make_fake_stdin():
    def _make_fake_stdin(isatty: bool = True, initial_value: str = ""):
        return FakeStdin(isatty=isatty, initial_value=initial_value)

    return _make_fake_stdin


class FakeClipboard:
    """Mimics the pyperclip.paste function for testing purposes."""

    def __init__(self, initial_value: str = ""):
        self._value = initial_value

    def paste(self):
        return self._value


@pytest.fixture
def make_fake_clipboard():
    def _make_fake_clipboard(initial_value: str = ""):
        return FakeClipboard(initial_value)

    return _make_fake_clipboard


class FakeSessionFactory:
    """Mimics the minimal required portion of the  requests.Session interface for
    testing purposes (and it stores the last request sent through it).
    """

    def __init__(self, response_content=None, response_headers=None):
        self.sent_request: requests.Request = requests.Request()
        self._response_content = response_content or b"fake response"
        self._response_headers = response_headers or {}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def send(self, request: requests.Request) -> requests.Response:
        self.sent_request = request
        response = requests.Response()
        response._content = self._response_content
        response.headers.update(self._response_headers)
        response.status_code = 200
        return response


@pytest.fixture
def fake_session():
    return FakeSessionFactory()


@pytest.mark.parametrize(
    ["content_type", "content", "expected_is_binary", "test_id"],
    [
        # Text content types (should not be binary)
        ('text/html', b"Hello, world!", False, "text_html"),
        ('application/json', b'{"key": "value"}', False, "json"),
        ('application/xml', b'<?xml version="1.0"?><root>test</root>', False, "xml"),
        ('application/xhtml+xml', b'<!DOCTYPE html><html><body>test</body></html>', False, "xhtml"),
        ('application/yaml', b'key: value\nlist:\n  - item1\n  - item2', False, "yaml"),
        ('text/plain', b'Plain text content', False, "text_plain"),
        ('application/javascript', b'console.log("hello");', False, "javascript"),

        # Binary content types (should be binary)
        ('image/png', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR', True, "png_image"),
        ('application/octet-stream', b'\x89\xff\xfe\x00', True, "octet_stream_invalid_utf8"),
        ('image/jpeg', b'\xff\xd8\xff\xe0', True, "jpeg_image"),
        ('application/pdf', b'%PDF-1.4\x89\xff\xfe\x00', True, "pdf"),

        # Unknown content types with valid UTF-8 (should not be binary)
        ('application/unknown', b'Hello, world!', False, "unknown_type_valid_utf8"),
        ('application/mystery', b'Valid text content', False, "mystery_type_valid_utf8"),

        # Unknown content types with invalid UTF-8 (should be binary)
        ('application/unknown', b'\x89\xff\xfe\x00', True, "unknown_type_invalid_utf8"),

        # No content type header with valid UTF-8 (should not be binary)
        ('', b'Hello, world!', False, "no_content_type_valid_utf8"),

        # No content type header with invalid UTF-8 (should be binary)
        ('', b'\x89\xff\xfe\x00', True, "no_content_type_invalid_utf8"),
    ]
)
def test_is_binary_response(content_type, content, expected_is_binary, test_id):
    """Test binary response detection for various content types and content."""
    response = requests.Response()
    response._content = content
    if content_type:
        response.headers['Content-Type'] = content_type

    assert _is_binary_response(response) == expected_is_binary


def test_binary_response_output(
    make_fake_stdin,
    make_fake_clipboard,
    capfdbinary,
):
    """Test that binary responses are handled without errors."""
    binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
    fake_session = FakeSessionFactory(
        response_content=binary_content,
        response_headers={'Content-Type': 'image/png'}
    )

    exit_code = main(
        cmd_line_args=["localcurl", "http://localhost:8080/", "curl", "https://example.com"],
        stdin=make_fake_stdin(),
        clipboard=make_fake_clipboard(),
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0
    assert capfdbinary.readouterr().out == binary_content

def test_text_response_output(
    make_fake_stdin,
    make_fake_clipboard,
    capsys,
):
    """Test that text responses are printed normally."""
    text_content = b"Hello, world!"
    fake_session = FakeSessionFactory(
        response_content=text_content,
        response_headers={'Content-Type': 'text/plain'}
    )

    exit_code = main(
        cmd_line_args=["localcurl", "http://localhost:8080/", "curl", "https://example.com"],
        stdin=make_fake_stdin(),
        clipboard=make_fake_clipboard(),
        session_factory=lambda: fake_session,
    )

    assert exit_code == 0
    captured = capsys.readouterr()
    assert captured.out == "Hello, world!"
    assert captured.err == ""
