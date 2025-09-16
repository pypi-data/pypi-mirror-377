"""LeagueWizard main entry point."""

import asyncio
import os
import socket
import tempfile
import threading
import urllib
from pathlib import Path
from typing import Any

import pystray
from loguru import logger
from PIL import Image

from leaguewizard.core import start
from leaguewizard.exceptions import LeWizardGenericError

base_dir = os.getenv("LOCALAPPDATA", "tempfile.gettempdir()")
lewizard_dir = Path(base_dir, "LeagueWizard")
log_dir = Path(lewizard_dir, "logs")
log_dir.mkdir(parents=True, exist_ok=True)


def to_tray() -> Any:
    """Create the tray icon with exit action.

    Returns:
        Any: Must be a pystray Icon object.
    """
    dest = f"{tempfile.gettempdir()}\\logo.png"
    urllib.request.urlretrieve(
        "https://github.com/amburgao/leaguewizard/blob/main/.github/images/logo.png?raw=true",
        dest,
    )
    return pystray.Icon(
        (0, 0),
        icon=Image.open(dest),
        menu=pystray.Menu(pystray.MenuItem("Exit", lambda icon, item: os._exit(0))),
    )


def main() -> None:
    logger.add(f"{log_dir}/log.txt", rotation="1MB")

    """LeagueWizard main entry point function."""
    s = socket.socket()
    try:
        s.bind(("127.0.0.1", 54321))
    except OSError as e:
        raise LeWizardGenericError(
            message="Another instance is already running",
            show=True,
            title="Error!",
            exit=True,
        ) from e

    tray = to_tray()
    tray_thread = threading.Thread(target=tray.run, daemon=True)
    tray_thread.start()

    asyncio.run(start())
    tray.stop()


if __name__ == "__main__":
    main()
