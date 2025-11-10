import socket
import time
import heroku3

import config
from .logging import LOGGER

HAPP = None
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


# Heroku git push command parts (used by update system)
XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "master",
]


def heroku():
    """Initialize Heroku app connection if valid API and app name exist."""
    global HAPP
    if is_heroku():
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info("✦ ʜᴇʀᴏᴋᴜ ᴀᴘᴘ ᴄᴏɴꜰɪɢᴜʀᴇᴅ...💙")
            except BaseException:
                LOGGER(__name__).warning(
                    "✦ ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜʀ ʜᴇʀᴏᴋᴜ ᴀᴘɪ ᴋᴇʏ ᴀɴᴅ ᴀᴘᴘ ɴᴀᴍᴇ ᴀʀᴇ ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴄᴏʀʀᴇᴄᴛʟʏ...💚"
                )
