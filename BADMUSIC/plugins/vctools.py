import logging
import uuid

from typing import List, Optional, Union

from pyrogram import filters, Client
from pyrogram.errors.exceptions.bad_request_400 import ChatAdminRequired as ChatAdminRequiredException
from pyrogram.raw import base
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import (
    CreateGroupCall,
    DiscardGroupCall,
    ExportGroupCallInvite,
    GetGroupParticipants,
)
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.types.user_and_chats import ChatPrivileges
from pyrogram.types import Message

from BADMUSIC.utils import admin_check
from BADMUSIC.utils.database import get_assistant
from BADMUSIC import app, Bad, config


other_filters = filters.group & ~filters.via_bot & ~filters.forwarded
other_filters2 = filters.private & ~filters.via_bot & ~filters.forwarded


def command(commands: Union[str, List[str]]):
    return filters.command(commands, "")


async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    assistant = await get_assistant(message.chat.id)
    chat_peer = await assistant.resolve_peer(message.chat.id)
    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (
                await assistant.invoke(GetFullChannel(channel=chat_peer))
            ).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (
                await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))
            ).full_chat
        if full_chat is not None:
            return full_chat.call
    await app.send_message(message.chat.id, f"**No group ᴠᴏɪᴄᴇ ᴄʜᴀᴛ Found{err_msg}**")
    return False


@app.on_message(filters.command(["vcstart", "startvc", "vcon"], ["/", "!"]))
async def start_group_call(c: Client, m: Message):
    logging.info(f"startvc called: {m.command}")
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    if assistant is None:
        await app.send_message(chat_id, "ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    ass = await assistant.get_me()
    assid = ass.id
    msg = await app.send_message(chat_id, "ꜱᴛᴀʀᴛɪɴɢ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ..")
    call_name = m.text.split(maxsplit=1)[1] if len(m.command) > 1 else " VC"
    try:
        peer = await assistant.resolve_peer(chat_id)
        await assistant.invoke(
            CreateGroupCall(
                peer=peer,
                random_id=assistant.rnd_id() // 9000000000,
                title=call_name,
            )
        )
        await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
    except ChatAdminRequiredException:
        try:
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=True,
                    can_restrict_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                ),
            )
            peer = await assistant.resolve_peer(chat_id)
            await assistant.invoke(
                CreateGroupCall(
                    peer=peer,
                    random_id=assistant.rnd_id() // 9000000000,
                    title=call_name,
                )
            )
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                ),
            )
            await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ꜱᴛᴀʀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
        except Exception as e:
            await msg.edit_text(f"ᴘʟᴇᴀꜱᴇ ᴍᴀᴋᴇ ᴍᴇ ᴀᴅᴍɪɴ ᴡɪᴛʜ ᴍᴀɴᴀɢᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ ᴀɴᴅ ᴀᴅᴅ ɴᴇᴡ ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ.\nᴇʀʀᴏʀ: {e}")
    except Exception as e:
        await msg.edit_text(
            f"ɢɪᴠᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assid}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ.\nᴇʀʀᴏʀ: {e}"
        )


@app.on_message(filters.command("endvc", ["/", "!"]) & admin_check)
async def stop_group_call(c: Client, m: Message):
    logging.info(f"endvc called: {m.command}")
    chat_id = m.chat.id
    assistant = await get_assistant(chat_id)
    if assistant is None:
        await app.send_message(chat_id, "ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    ass = await assistant.get_me()
    assid = ass.id
    msg = await app.send_message(chat_id, "ᴄʟᴏꜱɪɴɢ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ..")
    try:
        if not (
            group_call := (
                await get_group_call(
                    assistant, m, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ"
                )
            )
        ):
            return
        await assistant.invoke(DiscardGroupCall(call=group_call))
        await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄʟᴏꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
    except ChatAdminRequiredException:
        try:
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=True,
                    can_restrict_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                ),
            )
            if not (
                group_call := (
                    await get_group_call(
                        assistant, m, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ"
                    )
                )
            ):
                return
            await assistant.invoke(DiscardGroupCall(call=group_call))
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatPrivileges(
                    can_manage_chat=False,
                    can_delete_messages=False,
                    can_manage_video_chats=False,
                    can_restrict_members=False,
                    can_change_info=False,
                    can_invite_users=False,
                    can_pin_messages=False,
                    can_promote_members=False,
                ),
            )
            await msg.edit_text("ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴄʟᴏꜱᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ⚡️~!")
        except Exception as e:
            await msg.edit_text(f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assid}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ")
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await msg.edit_text("**ᴠᴄ ɪꜱ ᴀʟʀᴇᴀᴅʏ ᴏꜰꜰ ʙᴀʙʏ**")
        elif "GROUPCALL_FORBIDDEN" in str(e):
            await msg.edit_text(
                f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assid}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
            )
        else:
            logging.exception(e)
            await msg.edit_text(str(e))


@app.on_message(filters.command("vclink", ["/", "!"]) & admin_check)
async def vclink(client, message: Message):
    logging.info(f"vclink called: {message.command}")
    chat_id = message.chat.id
    assistant = await get_assistant(chat_id)
    if assistant is None:
        await message.reply("ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    ass = await assistant.get_me()
    assid = ass.id
    hell = await message.reply_text("ɢᴇᴛᴛɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ʟɪɴᴋ...")

    try:
        if not (
            group_call := (
                await get_group_call(
                    assistant, message, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ"
                )
            )
        ):
            return

        # To get the invite, we need to re-fetch full_chat since get_group_call only returns call
        chat_peer = await assistant.resolve_peer(chat_id)
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (await assistant.invoke(GetFullChannel(channel=chat_peer))).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))).full_chat
        else:
            await hell.edit_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ/ᴄʜᴀɴɴᴇʟꜱ")
            return
        invite = await assistant.invoke(ExportGroupCallInvite(call=full_chat.call))
        await hell.edit_text(f"ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ʟɪɴᴋ: {invite.link}")

    except ChatAdminRequiredException:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assid}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
        )
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("ᴠᴄ ɪꜱ  ᴏꜰꜰ ʙᴀʙʏ")
        else:
            logging.exception(e)
            await hell.edit_text(str(e))


@app.on_message(filters.command("vcuser", ["/", "!"]))
async def vcmembers(client, message: Message):
    logging.info(f"vcuser called: {message.command}")
    chat_id = message.chat.id
    assistant = await get_assistant(chat_id)
    if assistant is None:
        await message.reply("ᴇʀʀᴏʀ ᴡɪᴛʜ ᴀꜱꜱɪꜱᴛᴀɴᴛ")
        return
    ass = await assistant.get_me()
    assid = ass.id
    hell = await message.reply_text("ɢᴇᴛᴛɪɴɢ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴍᴇᴍʙᴇʀꜱ...")

    try:
        if not (
            group_call := (
                await get_group_call(
                    assistant, message, err_msg=", ɢʀᴏᴜᴘ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴀʟʀᴇᴀᴅʏ ᴇɴᴅᴇᴅ"
                )
            )
        ):
            return

        # To get participants, we need to re-fetch full_chat since get_group_call only returns call
        chat_peer = await assistant.resolve_peer(chat_id)
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (await assistant.invoke(GetFullChannel(channel=chat_peer))).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))).full_chat
        else:
            await hell.edit_text("ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ/ᴄʜᴀɴɴᴇʟꜱ")
            return
        participants = await assistant.invoke(
            GetGroupParticipants(
                call=full_chat.call,
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

    except ChatAdminRequiredException:
        await hell.edit_text(
            f"ɢɪᴠᴇ ᴍᴇ ᴍᴀɴᴀɢᴇ ᴠᴄ ᴘᴏᴡᴇʀ ᴛᴏ ᴍʏ [ᴀꜱꜱɪꜱᴛᴀɴᴛ](tg://openmessage?user_id={assid}) ɪɴꜱᴛᴇᴀᴅ ᴛᴏ ᴜꜱᴇ ᴛʜɪꜱ ᴄᴏᴍᴍᴀɴᴅ"
        )
    except Exception as e:
        if "'NoneType' object has no attribute 'write'" in str(e):
            await hell.edit_text("ᴠᴄ ɪꜱ  ᴏꜰꜰ ʙᴀʙʏ")
        else:
            logging.exception(e)
            await hell.edit_text(str(e))
