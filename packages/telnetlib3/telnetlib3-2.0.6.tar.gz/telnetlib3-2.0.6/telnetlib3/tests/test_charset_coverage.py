"""Test CHARSET functionality with comprehensive coverage."""

# std imports
import asyncio
import pytest
import codecs

# local imports
import telnetlib3
from telnetlib3.tests.accessories import unused_tcp_port, bind_host


class CustomTelnetClient(telnetlib3.TelnetClient):
    """Test client with controlled send_charset() behavior."""
    
    def __init__(self, *args, **kwargs):
        self.charset_behavior = kwargs.pop('charset_behavior', None)
        self.charset_response = kwargs.pop('charset_response', None)
        super().__init__(*args, **kwargs)

    def send_charset(self, offered):
        """Override to allow testing specific behavior branches."""
        if self.charset_behavior == 'unknown_encoding':
            # Test LookupError handling with explicit encoding
            self.default_encoding = 'unknown-encoding-xyz'
            return super().send_charset(offered)
        elif self.charset_behavior == 'no_viable_offers':
            # Return empty offers list to test no viable offers path
            return super().send_charset([])
        elif self.charset_behavior == 'explicit_non_latin1':
            # Test rejection when explicit encoding isn't offered
            self.default_encoding = 'utf-16'
            return super().send_charset(['utf-8', 'ascii'])
        elif self.charset_response is not None:
            # Return a predetermined response
            return self.charset_response
        else:
            return super().send_charset(offered)


async def test_charset_send_unknown_encoding(bind_host, unused_tcp_port):
    """Test client with unknown encoding value."""
    # Given a client with an unknown encoding, it should handle LookupError
    _waiter = asyncio.Future()

    await asyncio.get_event_loop().create_server(
        asyncio.Protocol, bind_host, unused_tcp_port
    )

    reader, writer = await telnetlib3.open_connection(
        client_factory=lambda **kwargs: CustomTelnetClient(
            charset_behavior='unknown_encoding', **kwargs
        ),
        host=bind_host,
        port=unused_tcp_port,
        connect_minwait=0.05
    )
    
    # Verify behavior - mainly we're checking that this doesn't raise an exception
    assert writer.protocol.encoding(incoming=True) == "US-ASCII"


async def test_charset_send_no_viable_offers(bind_host, unused_tcp_port):
    """Test client with no viable encoding offers."""
    _waiter = asyncio.Future()

    await asyncio.get_event_loop().create_server(
        asyncio.Protocol, bind_host, unused_tcp_port
    )

    reader, writer = await telnetlib3.open_connection(
        client_factory=lambda **kwargs: CustomTelnetClient(
            charset_behavior='no_viable_offers', **kwargs
        ),
        host=bind_host,
        port=unused_tcp_port,
        connect_minwait=0.05
    )
    
    # Verify behavior - this should stick with the default encoding
    assert writer.protocol.encoding(incoming=True) == "US-ASCII"


async def test_charset_explicit_non_latin1_encoding(bind_host, unused_tcp_port):
    """Test client rejecting offered encodings when explicit non-latin1 is set."""
    _waiter = asyncio.Future()

    await asyncio.get_event_loop().create_server(
        asyncio.Protocol, bind_host, unused_tcp_port
    )

    reader, writer = await telnetlib3.open_connection(
        client_factory=lambda **kwargs: CustomTelnetClient(
            charset_behavior='explicit_non_latin1', **kwargs
        ),
        host=bind_host,
        port=unused_tcp_port,
        connect_minwait=0.05
    )
    
    # Verify behavior - this should stick with the default encoding
    assert writer.protocol.encoding(incoming=True) == "US-ASCII"
