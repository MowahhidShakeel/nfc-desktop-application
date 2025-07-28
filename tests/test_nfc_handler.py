import pytest
from unittest.mock import Mock
from src.core.nfc_handler import NFCHandler

@pytest.fixture
def mock_nfc():
    nfc = NFCHandler()
    nfc.reader = Mock()
    nfc.connection = Mock()
    nfc.connection.transmit = Mock(return_value=([0x00, 0x00, 0x00, 0x00], 0x90, 0x00))
    return nfc

def test_connect(mock_nfc):
    assert mock_nfc.connect() is True

def test_write_page(mock_nfc):
    mock_nfc.connect()
    assert mock_nfc.write_page(4, [0x49, 192, 168, 1]) is True

def test_read_page(mock_nfc):
    mock_nfc.connect()
    data = mock_nfc.read_page(4)
    assert data == [0x00, 0x00, 0x00, 0x00]