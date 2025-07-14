import asyncio
import importlib

from Badmunda import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from BADMUSIC import LOGGER, app, userbot
from BADMUSIC.core.call import Bad
from BADMUSIC.misc import sudo
from BADMUSIC.plugins import ALL_MODULES
from BADMUSIC.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("✦ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴄʟɪᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇꜱ ɴᴏᴛ ᴅᴇꜰɪɴᴇᴅ, ᴇxɪᴛɪɴɢ...")
        exit()
    await sudo()
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass
    await app.start()
    for all_module in ALL_MODULES:
        importlib.import_module("BADMUSIC.plugins" + all_module)
    LOGGER("BADMUSIC.plugins").info("✦ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ɪᴍᴘᴏʀᴛᴇᴅ ᴍᴏᴅᴜʟᴇꜱ...💞")
    await userbot.start()
    await Bad.start()
    try:
        await Bad.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("BADMUSIC").error(
            "✦ ᴘʟᴇᴀꜱᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠɪᴅᴇᴏᴄʜᴀᴛ ᴏꜰ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ\ᴄʜᴀɴɴᴇʟ.\n\n✦ ꜱᴛᴏᴘᴘɪɴɢ ʙᴀᴅᴍᴜꜱɪᴄ ʙᴏᴛ...💣"
        )
        exit()
    except:
        pass
    await Bad.decorators()
    LOGGER("BADMUSIC").info(
        "✦ ᴄʀᴇᴀᴛᴇᴅ ʙʏ ➥ ʙᴀᴅ ᴍᴜɴᴅᴀ...🐝"
    )
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("BADMUSIC").info("❖ ꜱᴛᴏᴘᴘɪɴɢ ʙᴀᴅ ᴍᴜꜱɪᴄ ʙᴏᴛ...💌")


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(init())
