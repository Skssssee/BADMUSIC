import asyncio

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import InviteRequestSent

from BADMUSIC import Bad, app, config, userbot


links = {}


@app.on_message(filters.command(["ucjoin"]) & filters.user(app.owner))
async def join_group(client, message):
    chat_id = message.chat.id
    done = await message.reply("<b>ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ɪɴᴠɪᴛɪɴɢ ᴀssɪsᴛᴀɴᴛ</b>...")
    await asyncio.sleep(1)
    
    # Get chat member object for bot
    try:
        chat_member = await app.get_chat_member(chat_id, app.id)
    except Exception:
        await done.edit_text("<b>ᴜɴᴀʙʟᴇ ᴛᴏ ɢᴇᴛ ʙᴏᴛ sᴛᴀᴛᴜs.</b>")
        return
    
    is_bot_admin = chat_member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    has_username = bool(message.chat.username)
    assistant_id = userbot.me.id  # Assuming userbot is the client instance
    
    if not is_bot_admin:
        await done.edit_text("<b>ɪ ɴᴇᴇᴅ ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ᴛᴏ ɪɴᴠɪᴛᴇ ᴍʏ ᴀssɪsᴛᴀɴᴛ!</b>")
        return
    
    # Check if assistant is already a member
    try:
        assistant_member = await app.get_chat_member(chat_id, assistant_id)
        if assistant_member.status not in [ChatMemberStatus.BANNED, ChatMemberStatus.KICKED, ChatMemberStatus.RESTRICTED]:
            await done.edit_text("<b>✅ ᴀssɪsᴛᴀɴᴛ ᴀʟʀᴇᴀᴅʏ ᴊᴏɪɴᴇᴅ.</b>")
            return
        is_banned = True
    except Exception:
        is_banned = False
    
    if has_username:
        # Public group
        try:
            await userbot.join_chat(f"@{message.chat.username}")
            await done.edit_text("<b>✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ.</b>")
            return
        except InviteRequestSent:
            try:
                await app.approve_chat_join_request(chat_id, assistant_id)
                await done.edit_text("<b>✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ ᴠɪᴀ ᴀᴘᴘʀᴏᴠᴀʟ.</b>")
            except Exception:
                await done.edit_text("<b>ᴀᴘᴘʀᴏᴠᴀʟ ғᴀɪʟᴇᴅ, ᴘʟᴇᴀsᴇ ᴀᴘᴘʀᴏᴠᴇ ᴍᴀɴᴜᴀʟʟʏ.</b>")
            return
        except Exception as e:
            if is_banned:
                try:
                    await app.unban_chat_member(chat_id, assistant_id)
                    await asyncio.sleep(1)
                    await userbot.join_chat(f"@{message.chat.username}")
                    await done.edit_text("<b>ᴀssɪsᴛᴀɴᴛ ᴡᴀs ʙᴀɴɴᴇᴅ, ʙᴜᴛ ɴᴏᴡ ᴜɴʙᴀɴɴᴇᴅ ᴀɴᴅ ᴊᴏɪɴᴇᴅ ✅</b>")
                    return
                except Exception as e2:
                    await done.edit_text(f"<b>ғᴀɪʟᴇᴅ ᴛᴏ ᴜɴʙᴀɴ/ᴊᴏɪɴ: {str(e2)}</b>")
            else:
                await done.edit_text(f"<b>ᴇʀʀᴏʀ: {str(e)}</b>")
            return
    else:
        # Private group
        if is_banned:
            try:
                await app.unban_chat_member(chat_id, assistant_id)
                await done.edit_text("<b>ᴀssɪsᴛᴀɴᴛ ɪs ᴜɴʙᴀɴɴᴇᴅ. ᴛʏᴘᴇ /ᴜᴄᴊᴏɪɴ ᴀɢᴀɪɴ.</b>")
                # Recreate the function call or just return, but to chain, we'll proceed
            except Exception as e:
                await done.edit_text(
                    f"<b>➻ ᴀᴄᴛᴜᴀʟʟʏ ɪ ғᴏᴜɴᴅ ᴛʜᴀᴛ ᴍʏ ᴀssɪsᴛᴀɴᴛ ɪs ʙᴀɴɴᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ ᴀɴᴅ ɪ ᴀᴍ ɴᴏᴛ ᴀʙʟᴇ ᴛᴏ ᴜɴʙᴀɴ ᴍʏ ᴀssɪsᴛᴀɴᴛ ʙᴇᴄᴀᴜsᴇ [ ɪ ᴅᴏɴᴛ ʜᴀᴠᴇ ʙᴀɴ ᴘᴏᴡᴇʀ ] sᴏ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ʙᴀɴ ᴘᴏᴡᴇʀ ᴏʀ ᴜɴʙᴀɴ ᴍʏ ᴀssɪsᴛᴀɴᴛ ᴍᴀɴᴜᴀʟʟʏ ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ ʙʏ- /ᴜᴄᴊᴏɪɴ.</b>\n\n<b>➥ ɪᴅ »</b> @{userbot.me.username}"
                )
                return
        
        try:
            invite_link = await app.create_chat_invite_link(chat_id, expire_date=None)
            await asyncio.sleep(2)
            await userbot.join_chat(invite_link.invite_link)
            await done.edit_text("<b>✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>")
        except InviteRequestSent:
            try:
                await app.approve_chat_join_request(chat_id, assistant_id)
                await done.edit_text("<b>✅ ᴀssɪsᴛᴀɴᴛ ᴊᴏɪɴᴇᴅ ᴠɪᴀ ᴀᴘᴘʀᴏᴠᴀʟ.</b>")
            except Exception:
                await done.edit_text("<b>ᴀᴘᴘʀᴏᴠᴀʟ ғᴀɪʟᴇᴅ, ᴘʟᴇᴀsᴇ ᴀᴘᴘʀᴏᴠᴇ ᴍᴀɴᴜᴀʟʟʏ.</b>")
        except Exception as e:
            await done.edit_text(
                f"<b>➻ ᴀᴄᴛᴜᴀʟʟʏ ɪ ғᴏᴜɴᴅ ᴛʜᴀᴛ ᴍʏ ᴀssɪsᴛᴀɴᴛ ʜᴀs ɴᴏᴛ ᴊᴏɪɴᴇᴅ ᴛʜɪs ɢʀᴏᴜᴘ ᴀɴᴅ ɪ ᴀᴍ ɴᴏᴛ ᴀʙʟᴇ ᴛᴏ ɪɴᴠɪᴛᴇ ᴍʏ ᴀssɪsᴛᴀɴᴛ ʙᴇᴄᴀᴜsᴇ [ ɪ ᴅᴏɴᴛ ʜᴀᴠᴇ ɪɴᴠɪᴛᴇ ᴜsᴇʀ ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ] sᴏ ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ ᴍᴇ ɪɴᴠɪᴛᴇ ᴜsᴇʀs ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ᴛʜᴇɴ ᴛʀʏ ᴀɢᴀɪɴ ʙʏ- /ᴜᴄᴊᴏɪɴ.</b>\n\n<b>➥ ɪᴅ »</b> @{userbot.me.username}"
            )


@app.on_message(filters.command(["uleave"]) & filters.user(app.owner))
async def leave_one(client, message):
    try:
        await userbot.leave_chat(message.chat.id)
        await app.send_message(
            message.chat.id, "<b>✅ ᴜsᴇʀʙᴏᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ʟᴇғᴛ ᴛʜɪs Chat.</b>"
        )
    except Exception as e:
        print(e)
        await message.reply(f"<b>ᴇʀʀᴏʀ: {str(e)}</b>")


@app.on_message(filters.command(["lall"]) & filters.user(app.owner))
async def leave_all(client, message):
    # Assuming SUDOERS is defined in config or BADMUSIC, e.g., config.SUDOERS
    # If not, replace with appropriate variable
    if message.from_user.id not in config.SUDOERS:  # Adjust if needed
        await message.reply("<b>ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀᴜᴛʜᴏʀɪᴢᴇᴅ!</b>")
        return

    left = 0
    failed = 0
    lol = await message.reply("🔄 <b>ᴜsᴇʀʙᴏᴛ</b> ʟᴇᴀᴠɪɴɢ ᴀʟʟ ᴄʜᴀᴛs !")
    try:
        async for dialog in userbot.get_dialogs():
            if dialog.chat.id == -1002056907061:
                continue
            try:
                await userbot.leave_chat(dialog.chat.id)
                left += 1
                await lol.edit(
                    f"<b>ᴜsᴇʀʙᴏᴛ ʟᴇᴀᴠɪɴɢ ᴀʟʟ ɢʀᴏᴜᴘ...</b>\n\n<b>ʟᴇғᴛ:</b> {left} ᴄʜᴀᴛs.\n<b>ғᴀɪʟᴇᴅ:</b> {failed} ᴄʜᴀᴛs."
                )
            except Exception:
                failed += 1
                await lol.edit(
                    f"<b>ᴜsᴇʀʙᴏᴛ ʟᴇᴀᴠɪɴɢ...</b>\n\n<b>ʟᴇғᴛ:</b> {left} chats.\n<b>ғᴀɪʟᴇᴅ:</b> {failed} chats."
                )
            await asyncio.sleep(3)
    finally:
        await app.send_message(
            message.chat.id,
            f"<b>✅ ʟᴇғᴛ ғʀᴏᴍ:</b> {left} chats.\n<b>❌ ғᴀɪʟᴇᴅ ɪɴ:</b> {failed} chats.",
        )
