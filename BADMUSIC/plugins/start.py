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
            if await db.is_logger():
                chat = message.chat
                count = await app.get_chat_members_count(chat.id)
                username = f"@{chat.username}" if chat.username else "Private Chat"
                added_by = (
                    f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
                    if message.from_user
                    else "Unknown User"
                )
                
                # Get logger message from default language (assuming logging is in default/english)
                logger_msg = lang.ENGLISH["logger_new_group"].format(
                    chat.title,
                    chat.id,
                    username,
                    count,
                    added_by
                )

                await app.send_message(
                    config.LOGGER_ID,
                    text=logger_msg,
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
                    userbot = await db.get_assistant(chat.id)
                    await userbot.join_chat(chat.username)

            # Welcome message in group
            if await db.is_chat(message.chat.id):
                return
            await utils.send_log(message, True)
            await db.add_chat(message.chat.id)

            # Get welcome message from default language
            key = buttons.start_key(lang.ENGLISH, False) 
            caption = lang.ENGLISH["group_welcome"].format(
                message.from_user.mention, 
                app.mention, 
                message.chat.title
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
    if not await db.is_logger():
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
        
        # Get logger message from default language
        left_msg = lang.ENGLISH["logger_group_leave"].format(
            chat.title,
            chat.id,
            username,
            remove_by
        )

        await app.send_message(
            config.LOGGER_ID,
            text=left_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 ᴠɪᴇᴡ ᴀᴅᴅᴇᴅ ᴜꜱᴇʀ", # Assuming this button text is constant
                            url=f"tg://user?id={message.from_user.id}",
                        )
                    ]
                ]
            ),
        )

        await db.rm_chat(chat.id)
        try:
            userbot = await db.get_assistant(chat.id)
            await userbot.leave_chat(chat.id)
        except:
            pass
            
