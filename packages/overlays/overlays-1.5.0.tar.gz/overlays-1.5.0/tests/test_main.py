from unittest.mock import patch

import pytest
from overlays import main


def test_exits_on_non_windows_platform(capsys):
    # Mock platform.system to return a non-Windows platform
    with patch("platform.system", return_value="Linux"):
        # Expect SystemExit to be raised with code 1
        with pytest.raises(SystemExit) as exc_info:
            main.cross_platform_helper()  # Call the main function directly

        # Verify the exit code is 1
        assert exc_info.value.code == 1

        # Capture the output and verify the error message
        captured = capsys.readouterr()
        assert (
            "❌ Error: This application is designed to run on Windows only."
            in captured.out
        )
