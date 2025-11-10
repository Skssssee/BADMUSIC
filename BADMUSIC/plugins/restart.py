import asyncio
import os
import sys
import shutil
import socket
from datetime import datetime

import urllib3
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError
from pyrogram import filters, types

from BADMUSIC import config, app, db, lang
from BADMUSIC.utils.misc import HAPP, XCB, BadBin

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


async def is_heroku():
    return "heroku" in socket.getfqdn()


@app.on_message(filters.command(["gitpull"]) & app.sudoers)
async def update_(client, message):
    if await is_heroku() and HAPP is None:
        return await message.reply_text("ʜᴇʀᴏᴋᴜ ᴀᴘᴘ ᴄᴏɴғɪɢ ᴍɪssɪɴɢ.")

    response = await message.reply_text("ғᴇᴛᴄʜɪɴɢ ʟᴀᴛᴇsᴛ ᴜᴘᴅᴀᴛᴇs...")

    try:
        repo = Repo()
    except GitCommandError:
        return await response.edit("ɢɪᴛ ᴄᴏᴍᴍᴀɴᴅ ᴇʀʀᴏʀ — ᴍᴀʏʙᴇ ʀᴇᴘᴏ ɴᴏᴛ ɪɴɪᴛɪᴀʟɪᴢᴇᴅ ᴘʀᴏᴘᴇʀʟʏ.")
    except InvalidGitRepositoryError:
        return await response.edit("ɪɴᴠᴀʟɪᴅ ɢɪᴛ ʀᴇᴘᴏsɪᴛᴏʀʏ.")

    os.system(f"git fetch origin {config.UPSTREAM_BRANCH} &> /dev/null")
    await asyncio.sleep(7)

    repo_url = repo.remotes.origin.url.split(".git")[0]
    commits = list(repo.iter_commits(f"HEAD..origin/{config.UPSTREAM_BRANCH}"))

    if not commits:
        return await response.edit("✅ ʙᴏᴛ ɪs ᴀʟʀᴇᴀᴅʏ ᴜᴘ ᴛᴏ ᴅᴀᴛᴇ!")

    updates = ""
    for info in commits:
        updates += (
            f"<b>➣ ᴄᴏᴍᴍɪᴛ:</b> <a href={repo_url}/commit/{info}>{info.summary}</a>\n"
            f"<b>ʙʏ:</b> {info.author}\n"
            f"<b>ᴅᴀᴛᴇ:</b> {datetime.fromtimestamp(info.committed_date).strftime('%d %b %Y')}\n\n"
        )

    header = "<b>🚀 ɴᴇᴡ ᴜᴘᴅᴀᴛᴇs ᴀᴠᴀɪʟᴀʙʟᴇ ғᴏʀ ᴛʜᴇ ʙᴏᴛ!</b>\n\n"
    final_text = header + updates

    if len(final_text) > 4096:
        url = await BadBin(updates)
        await response.edit(f"🚀 ɴᴇᴡ ᴜᴘᴅᴀᴛᴇs ᴀᴠᴀɪʟᴀʙʟᴇ!\n\n<a href={url}>ᴠɪᴇᴡ ғᴜʟʟ ᴄʜᴀɴɢᴇʟᴏɢ</a>", disable_web_page_preview=True)
    else:
        await response.edit(final_text, disable_web_page_preview=True)

    os.system("git stash &> /dev/null && git pull")

    if await is_heroku():
        try:
            os.system(
                f"{XCB[5]} {XCB[7]} {XCB[9]}{XCB[4]}{XCB[0]*2}{XCB[6]}{XCB[4]}{XCB[8]}{XCB[1]}{XCB[5]}{XCB[2]}{XCB[6]}{XCB[2]}{XCB[3]}{XCB[0]}{XCB[10]}{XCB[2]}{XCB[5]} {XCB[11]}{XCB[4]}{XCB[12]}"
            )
        except Exception as err:
            await app.send_message(config.LOGGER_ID, f"⚠️ ᴜᴘᴅᴀᴛᴇ ғᴀɪʟᴇᴅ:\n{err}")
    else:
        os.system("pip3 install -r requirements.txt")
        os.system(f"kill -9 {os.getpid()} && bash start")
        exit()


@app.on_message(filters.command(["logs"]) & app.sudoers)
@lang.language()
async def _logs(_, m: types.Message):
    sent = await m.reply_text(m.lang["log_fetch"])
    if not os.path.exists("log.txt"):
        return await sent.edit_text(m.lang["log_not_found"])
    await sent.edit(
        media=types.InputMediaDocument(
            media="log.txt",
            caption=m.lang["log_sent"].format(app.name),
        )
    )


@app.on_message(filters.command(["logger"]) & app.sudoers)
@lang.language()
async def _logger(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))
    if m.command[1] not in ("on", "off"):
        return await m.reply_text(m.lang["logger_usage"].format(m.command[0]))

    if m.command[1] == "on":
        await db.set_logger(True)
        await m.reply_text(m.lang["logger_on"])
    else:
        await db.set_logger(False)
        await m.reply_text(m.lang["logger_off"])


@app.on_message(filters.command(["restart"]) & app.sudoers)
@lang.language()
async def _restart(_, m: types.Message):
    sent = await m.reply_text(m.lang["restarting"])

    for directory in ["downloads", "cache"]:
        try:
            shutil.rmtree(directory)
        except:
            pass

    await sent.edit_text(m.lang["restarted"])

    try:
        await app.exit()
        await userbot.exit()
        await db.close()
    except:
        pass

    for task in tasks:
        task.cancel()
        try:
            await task
        except:
            pass    

    os.execl(sys.executable, sys.executable, "-m", "BADMUSIC")
