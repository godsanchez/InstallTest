import os
import sys

# The module parses CLI args at import time, so provide a clean argv first.
sys.argv = ["downloadblob.py"]

import downloadblob


def test_download_root_path():
    """DOWNLOAD_ROOT should point at the CRC/Packages directory."""
    assert downloadblob.DOWNLOAD_ROOT.endswith(os.path.join("CRC", "Packages"))
