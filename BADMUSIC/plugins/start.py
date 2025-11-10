from pyrogram import enums, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
import random

from BADMUSIC import app, config, db, lang
from BADMUSIC.utils import buttons, utils


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    await m.reply_photo(
        photo=random.choice(config.HELP_IMG),
        caption=m.lang["help_menu"],
        reply_markup=buttons.help_markup(m.lang),
        quote=True,
        has_spoiler=True,
    )


@app.on_message(filters.command(["help"]) & filters.group & ~app.bl_users)
@lang.language()
async def group_help(_, message: types.Message):
    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("• ʜᴇʟᴘ ᴧɴᴅ ᴄᴏᴍᴍᴧɴᴅs •", url=f"https://t.me/{app.username}?start=help")]]
    )
    await message.reply_text(
        "ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴜᴛᴛᴏɴ ʙᴇʟᴏᴡ ᴛᴏ ɢᴇᴛ ᴍʏ ʜᴇʟᴘ ᴍᴇɴᴜ ɪɴ ʏᴏᴜʀ ᴘᴍ.",
        reply_markup=markup,
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    if message.from_user.id in app.bl_users and message.from_user.id not in db.notified:
        return await message.reply_text(message.lang["bl_user_notify"])

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE
    _text = (
        message.lang["start_pm"].format(message.from_user.first_name, app.name)
        if private
        else message.lang["start_gp"].format(app.name)
    )

    key = buttons.start_key(message.lang, private)
    await message.reply_photo(
        photo=random.choice(config.START_IMG),
        caption=_text,
        reply_markup=key,
        quote=not private,
        has_spoiler=True,
    )

    if private:
        if await db.is_user(message.from_user.id):
            return
        await utils.send_log(message)
        return await db.add_user(message.from_user.id)


@app.on_message(filters.command(["playmode", "settings"]) & filters.group & ~app.bl_users)
@lang.language()
async def settings(_, message: types.Message):
    admin_only = await db.get_play_mode(message.chat.id)
    _language = await db.get_lang(message.chat.id)
    await message.reply_text(
        text=message.lang["start_settings"].format(message.chat.title),
        reply_markup=buttons.settings_markup(
            message.lang, admin_only, _language, message.chat.id
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=-1)
async def on_new_member(_, message: Message):
    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    for member in message.new_chat_members:
        if member.id == app.id:
            # Logging for bot added
            if not await db.is_on_off(config.LOG):  # Assuming db.is_on_off and config.LOG exist
                pass
            else:
                chat = message.chat
                count = await app.get_chat_members_count(chat.id)
                username = f"@{chat.username}" if chat.username else "Private Chat"
                added_by = (
                    f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
                    if message.from_user
                    else "Unknown User"
                )
                msg = (
                    "🎉 <b><u>Mᴜsɪᴄ Bᴏᴛ Aᴅᴅᴇᴅ ɪɴ #New_Group</u></b> 🎉\n\n"
                    f"• <b>Chat Name:</b> <code>{chat.title}</code>\n"
                    f"• <b>Chat ID:</b> <code>{chat.id}</code>\n"
                    f"• <b>Chat Username:</b> <code>{username}</code>\n"
                    f"• <b>Total Members:</b> <code>{count}</code>\n"
                    f"• <b>Added:</b> {added_by}"
                )

                await app.send_message(
                    config.LOGGER_ID,
                    text=msg,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="👤 ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴜꜱᴇʀ",
                                    url=f"tg://user?id={message.from_user.id}",
                                )
                            ]
                        ]
                    ),
                )

                if chat.username:
                    userbot = await db.get_assistant(chat.id)  # Assuming db.get_assistant exists
                    await userbot.join_chat(chat.username)

            # Welcome message in group
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)

            # Send welcome photo
            key = buttons.start_key(lang.ENGLISH, False)  # Assuming default lang, adjust if needed
            caption = (
                f"ʜᴇʏ {message.from_user.mention},\n"
                f"ᴛʜɪs ɪs {app.mention}\n\n"
                f"ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ɪɴ {message.chat.title}, "
                f"{app.mention} ᴄᴀɴ ɴᴏᴡ ᴩʟᴀʏ sᴏɴɢs ɪɴ ᴛʜɪs ᴄʜᴀᴛ."
            )
            await message.reply_photo(
                photo=random.choice(config.START_IMG),
                caption=caption,
                reply_markup=key,
                quote=False,
                has_spoiler=True,
            )
            return


@app.on_message(filters.left_chat_member)
async def on_bot_kicked(_, message: Message):
    if not await db.is_on_off(config.LOG):  # Assuming db.is_on_off and config.LOG exist
        return

    left_chat_member = message.left_chat_member
    if left_chat_member and left_chat_member.id == app.id:
        chat = message.chat
        remove_by = (
            f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            if message.from_user
            else "Unknown User"
        )
        username = f"@{chat.username}" if chat.username else "Private Chat"
        left_msg = (
            "❌ <b><u>Bᴏᴛ Rᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ Gʀᴏᴜᴘ #Left_group</u></b> ❌\n\n"
            f"• <b>Chat Name:</b> <code>{chat.title}</code>\n"
            f"• <b>Chat ID:</b> <code>{chat.id}</code>\n"
            f"• <b>Chat Username:</b> <code>{username}</code>\n"
            f"• <b>Removed:</b> {remove_by}"
        )

        await app.send_message(
            config.LOGGER_ID,
            text=left_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴜꜱᴇʀ",
                            url=f"tg://user?id={message.from_user.id}",
                        )
                    ]
                ]
            ),
        )

        await db.delete_served_chat(chat.id)  # Assuming db.delete_served_chat exists
        userbot = await db.get_assistant(chat.id)  # Assuming db.get_assistant exists
        await userbot.leave_chat(chat.id)
