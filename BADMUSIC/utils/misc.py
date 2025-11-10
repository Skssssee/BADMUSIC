import socket
import time
import heroku3

from BADMUSIC import config, logger

HAPP = None
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


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
                logger(__name__).info("✦ ʜᴇʀᴏᴋᴜ ᴀᴘᴘ ᴄᴏɴꜰɪɢᴜʀᴇᴅ...💙")
            except BaseException:
                logger(__name__).warning(
                    "✦ ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ꜱᴜʀᴇ ʏᴏᴜʀ ʜᴇʀᴏᴋᴜ ᴀᴘɪ ᴋᴇʏ ᴀɴᴅ ᴀᴘᴘ ɴᴀᴍᴇ ᴀʀᴇ ᴄᴏɴꜰɪɢᴜʀᴇᴅ ᴄᴏʀʀᴇᴄᴛʟʏ...💚"
                )


import aiohttp

BASE = "https://batbin.me/"


async def post(url: str, *args, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as resp:
            try:
                data = await resp.json()
            except Exception:
                data = await resp.text()
        return data


async def BadBin(text):
    resp = await post(f"{BASE}api/v2/paste", data=text)
    if not resp["success"]:
        return
    link = BASE + resp["message"]
    return link
