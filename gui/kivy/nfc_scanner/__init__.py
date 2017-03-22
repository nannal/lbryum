__all__ = ('NFCBase', 'NFCScanner')

# load NFCScanner implementation

NFCScanner = core_select_lib('nfc_manager', (
    # keep the dummy implementtation as the last one to make it the fallback provider.NFCScanner = core_select_lib('nfc_scanner', (
    ('android', 'scanner_android', 'ScannerAndroid'),
    ('dummy', 'scanner_dummy', 'ScannerDummy')), True, 'electrum_gui.kivy')
