from pyrogram import filters, types

from BADMUSIC import Bad, app, db, lang, queue
from BADMUSIC.utils import can_manage_vc


@app.on_message(filters.command(["seek", "seekback"]) & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def _seek(_, m: types.Message):
    if len(m.command) < 2:
        return await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))

    try:
        to_seek = int(m.command[1])
    except ValueError:
        return await m.reply_text(m.lang["play_seek_usage"].format(m.command[0]))
    if to_seek < 10:
        return await m.reply_text(m.lang["play_seek_min"])

    if not await db.get_call(m.chat.id):
        return await m.reply_text(m.lang["not_playing"])

    if not await db.playing(m.chat.id):
        return await m.reply_text(m.lang["play_already_paused"])

    media = queue.get_current(m.chat.id)
    if not media.duration_sec:
        return await m.reply_text(m.lang["play_seek_no_dur"])

    sent = await m.reply_text(m.lang["play_seeking"])
    if m.command[0] == "seekback":
        stype = m.lang["backward"]
        start_from = media.time - to_seek
        if start_from < 1:
            start_from = 1
    else:
        stype = m.lang["forward"]
        start_from = media.time + to_seek
        if start_from + 10 > media.duration_sec:
            start_from = media.duration_sec - 5

    await Bad.play_media(m.chat.id, sent, media, start_from)
    media.time = start_from
    await sent.edit_text(
        m.lang["play_seeked"].format(stype, start_from, m.from_user.mention)
    )


@app.on_message(filters.command("bass") & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def bass_cmd(_, m: types.Message):
    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(m.lang.get("not_playing", "Nothing is playing!"))

    if not await db.playing(chat_id):
        return await m.reply_text(m.lang.get("play_already_paused", "Player is paused!"))

    current_effects = Bad.effects[chat_id]
    if len(m.command) == 1:
        level = current_effects['bass']
        status = "enabled" if level > 0 else "disabled"
        return await m.reply_text(f"Bass boost is {status} (gain: {level}dB)")

    if len(m.command) < 2:
        return await m.reply_text("Usage: /bass <0-50>")

    try:
        level = float(m.command[1])
        if level < 0 or level > 50:
            return await m.reply_text("Bass gain must be between 0 and 50 dB")
    except ValueError:
        return await m.reply_text("Invalid number for bass gain")

    current_effects['bass'] = level
    media = queue.get_current(chat_id)
    sent = await m.reply_text("Applying bass boost...")
    start_from = getattr(media, 'time', 0)
    await Bad.play_media(chat_id, sent, media, start_from)
    await sent.edit_text(f"Bass boost set to {level}dB")


@app.on_message(filters.command("speed") & filters.group & ~app.bl_users)
@lang.language()
@can_manage_vc
async def speed_cmd(_, m: types.Message):
    chat_id = m.chat.id
    if not await db.get_call(chat_id):
        return await m.reply_text(m.lang.get("not_playing", "Nothing is playing!"))

    if not await db.playing(chat_id):
        return await m.reply_text(m.lang.get("play_already_paused", "Player is paused!"))

    current_effects = Bad.effects[chat_id]
    if len(m.command) == 1:
        spd = current_effects['speed']
        return await m.reply_text(f"Current speed: {spd}x")

    if len(m.command) < 2:
        return await m.reply_text("Usage: /speed <0.25-2.0>")

    try:
        spd = float(m.command[1])
        if spd < 0.25 or spd > 2.0:
            return await m.reply_text("Speed must be between 0.25x and 2.0x")
    except ValueError:
        return await m.reply_text("Invalid number for speed")

    current_effects['speed'] = spd
    media = queue.get_current(chat_id)
    sent = await m.reply_text("Applying speed change...")
    start_from = getattr(media, 'time', 0)
    await Bad.play_media(chat_id, sent, media, start_from)
    await sent.edit_text(f"Speed set to {spd}x")
