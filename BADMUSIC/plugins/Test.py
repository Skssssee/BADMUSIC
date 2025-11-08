# bass.py (New file for bass boost command)
from pyrogram import filters, types

from BADMUSIC import Bad, app, db, lang, queue
from BADMUSIC.utils import can_manage_vc


@app.on_message(filters.command("bass") & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def set_bass(_, m: types.Message):
    chat_id = m.chat.id
    if len(m.command) < 2:
        current = await db.get_bass(chat_id) or 0
        return await m.reply_text(
            m.lang.get("bass_current", "Current Bass: {}").format(current) +
            "\nUsage: /bass <0-20> to set level (0 = off)"
        )

    try:
        level = int(m.command[1])
        if level < 0 or level > 20:
            return await m.reply_text(m.lang.get("bass_invalid", "Bass level must be 0-20"))
    except ValueError:
        return await m.reply_text(m.lang.get("bass_invalid", "Invalid number"))

    await db.set_bass(chat_id, level)
    await m.reply_text(m.lang.get("bass_set", "Bass set to {}").format(level))

    # Apply immediately if playing
    if await db.get_call(chat_id):
        media = queue.get_current(chat_id)
        if media:
            msg = await app.send_message(chat_id, m.lang.get("bass_applying", "Applying bass boost..."))
            await Bad.play_media(chat_id, msg, media, media.time)
            await msg.edit_text(m.lang.get("bass_applied", "Bass boost applied: {}").format(level))
