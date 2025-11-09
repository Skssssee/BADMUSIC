import asyncio
import importlib

from pyrogram import idle

from BADMUSIC import Bad, app, db, logger, tasks, userbot
from BADMUSIC.plugins import all_modules


async def main():
    await db.connect()
    await app.boot()
    await userbot.boot()
    await Bad.boot()

    for module in all_modules:
        importlib.import_module(f"BADMUSIC.plugins.{module}")
    logger.info(f"❖ ʟᴏᴀᴅᴇᴅ {len(all_modules)} ᴍᴏᴅᴜʟᴇꜱ 💫")

    sudoers = await db.get_sudoers()
    app.sudoers.update(sudoers)
    app.bl_users.update(await db.get_blacklisted())
    logger.info(f"❖ ʟᴏᴀᴅᴇᴅ {len(app.sudoers)} ꜱᴜᴅᴏ ᴜꜱᴇʀꜱ 🎉")

    await idle()
    logger.info("❖ ꜱᴛᴏᴘᴘɪɴɢ...😥")
    await app.exit()
    await userbot.exit()
    await db.close()
    for task in tasks:
        task.cancel()
        try:
            await task
        except:
            pass
    logger.info("❖ ꜱᴛᴏᴘᴘᴇᴅ😥")


if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        pass
