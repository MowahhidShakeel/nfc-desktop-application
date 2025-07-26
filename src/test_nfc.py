# src/test_nfc.py

from smartcard.System import readers

try:
    reader_list = readers()
    print('Connected readers:', reader_list)
except Exception as e:
    print('Error:', e)
