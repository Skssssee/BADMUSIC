import logging
import uuid

from pyrogram import filters
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired
from pyrogram.raw import base
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.phone import (
    CreateGroupCall,
    DiscardGroupCall,
    ExportGroupCallInvite,
    GetGroupParticipants,
)
from pyrogram.types import Message
from BADMUSIC.utils import admin_check
from BADMUSIC import Bad, app, config, userbot


@app.on_message(filters.command("startvc", "vcon"))
async def startvc(client, message: Message):

    call_name = message.text.split(maxsplit=1)[1] if len(message.command) > 1 else " VC"
    hell = await message.reply_text("ꜱᴛᴀʀᴛɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ...")
    if len(userbot.clients) == 0:
        await hell.edit_text("ɴᴏ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
    assistant = userbot.clients[0]

    try:
        await assistant.invoke(
            CreateGroupCall(
                peer=(await assistant.resolve_peer(message.chat.id)),
                random_id=int(str(uuid.uuid4().int)[:8]),
                title=call_name,
            )
        )

        await hell.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ!")

    except ChatAdminRequired:
        try:
            await app.promote_chat_member(
                message.chat.id, 
                assistant.id,  
                can_manage_video_chats=True,
            )
            await assistant.invoke(
                CreateGroupCall(
                    peer=(await assistant.resolve_peer(message.chat.id)),
                    random_id=int(str(uuid.uuid4().int)[:8]),
                    title=call_name,
                )
            )
            await hell.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ !")
            return
        except Exception as e:
            await hell.edit_text(
                f"ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴀɴᴅ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ.\nᴇʀʀᴏʀ: {e}"
            )
    except Exception as e:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assistant.id}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.\nᴇʀʀᴏʀ: {e}"
        )


@app.on_message(filters.command("endvc") & admin_check)
async def endvc(client, message: Message):
    hell = await message.reply_text("ᴇɴᴅɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ...")
    if len(userbot.clients) == 0:
        await hell.edit_text("ɴᴏ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
    assistant = userbot.clients[0]

    try:
        full_chat: base.messages.ChatFull = await assistant.invoke(
            GetFullChannel(channel=(await assistant.resolve_peer(message.chat.id)))
        )
        await assistant.invoke(DiscardGroupCall(call=full_chat.full_chat.call))
        await hell.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ!")
    except ChatAdminRequired:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assistant.id}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
        )
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("**ᴠᴄ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ ʙᴀʙʏ**")
        elif "phone.DiscardGroupCall" in str(e):
            await hell.edit_text(
                f"ɢɪᴠᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assistant.id}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
            )
        else:
            logging.exception(e)
            await hell.edit_text(e)


@app.on_message(filters.command("vclink") & admin_check)
async def vclink(client, message: Message):
    if len(userbot.clients) == 0:
        await message.reply("ɴᴏ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
    assistant = userbot.clients[0]
    hell = await message.reply_text("ɢᴇᴛᴛɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ʟɪɴᴋ...")

    try:
        full_chat: base.messages.ChatFull = await assistant.invoke(
            GetFullChannel(channel=(await assistant.resolve_peer(message.chat.id)))
        )

        invite: base.phone.ExportedGroupCallInvite = await assistant.invoke(
            ExportGroupCallInvite(call=full_chat.full_chat.call)
        )
        await hell.edit_text(f"ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ʟɪɴᴋ: {invite.link}")
    except ChatAdminRequired:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assistant.id}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
        )
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("ᴠᴄ ɪꜱ  ᴏꜰꜰ ʙᴀʙʏ")
        else:
            logging.exception(e)
            await hell.edit_text(e)


@app.on_message(filters.command("vcuser"))
async def vcmembers(client, message: Message):
    if len(userbot.clients) == 0:
        await message.reply("ɴᴏ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return
    assistant = userbot.clients[0]
    hell = await message.reply_text("ɢᴇᴛᴛɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ...")

    try:
        full_chat: base.messages.ChatFull = await assistant.invoke(
            GetFullChannel(channel=(await assistant.resolve_peer(message.chat.id)))
        )
        participants: base.phone.GroupParticipants = await assistant.invoke(
            GetGroupParticipants(
                call=full_chat.full_chat.call,
                ids=[],
                sources=[],
                offset="",
                limit=1000,
            )
        )
        count = participants.count
        text = f"ᴛᴏᴛᴀʟ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ: {count}\n"
        users = []
        for participant in participants.participants:
            users.append(participant.peer.user_id)
        for i in users:
            b = await app.get_users(i)
            text += f"[{b.first_name + (' ' + b.last_name if b.last_name else '')}](tg://user?id={b.id})\n"

        await hell.edit_text(text)
    except ChatAdminRequired:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assistant.id}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
        )
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("ᴠᴄ ɪꜱ  ᴏꜰꜰ ʙᴀʙʏ")
        else:
            logging.exception(e)
            await hell.edit_text(e)
