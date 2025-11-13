from typing import List, Optional, Union

from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.types import Message
from pyrogram.raw.types import ChatAdminRights

from BADMUSIC import app, db

# ==========================
#  Filters
# ==========================
other_filters = filters.group & ~filters.via_bot & ~filters.forwarded
other_filters2 = filters.private & ~filters.via_bot & ~filters.forwarded


def command(commands: Union[str, List[str]]):
    return filters.command(commands, "")


# ==========================
#  Helper to Get Group Call
# ==========================
async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    assistant = await db.get_assistant(message.chat.id)

    # Access Pyrogram client from PyTgCalls
    cli = getattr(assistant, "_client", None)
    if cli is None:
        await app.send_message(message.chat.id, "❌ Assistant client not found.")
        return False

    chat_peer = await cli.resolve_peer(message.chat.id)

    if isinstance(chat_peer, (InputPeerChannel, InputPeerChat)):
        if isinstance(chat_peer, InputPeerChannel):
            full_chat = (await cli.invoke(GetFullChannel(channel=chat_peer))).full_chat
        elif isinstance(chat_peer, InputPeerChat):
            full_chat = (await cli.invoke(GetFullChat(chat_id=chat_peer.chat_id))).full_chat
        if full_chat and getattr(full_chat, "call", None):
            return full_chat.call

    await app.send_message(message.chat.id, f"❌ No group voice chat found {err_msg}")
    return False


# ==========================
#  Start Group Call
# ==========================
@app.on_message(filters.command(["vcstart", "startvc"], ["/", "!"]))
async def start_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await db.get_assistant(chat_id)

    if assistant is None:
        return await app.send_message(chat_id, "❌ Error: Assistant not found!")

    cli = getattr(assistant, "_client", None)
    if cli is None:
        return await app.send_message(chat_id, "❌ Assistant Pyrogram client missing!")

    ass_user = await cli.get_me()
    assid = ass_user.id

    msg = await app.send_message(chat_id, "🎙 Starting the voice chat...")

    try:
        peer = await cli.resolve_peer(chat_id)
        await cli.invoke(
            CreateGroupCall(
                peer=InputPeerChannel(
                    channel_id=peer.channel_id,
                    access_hash=peer.access_hash,
                ),
                random_id=cli.rnd_id() // 9000000000,
            )
        )
        await msg.edit_text("✅ Voice chat started successfully ⚡️")
    except ChatAdminRequired:
        try:
            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatAdminRights(
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

            peer = await cli.resolve_peer(chat_id)
            await cli.invoke(
                CreateGroupCall(
                    peer=InputPeerChannel(
                        channel_id=peer.channel_id,
                        access_hash=peer.access_hash,
                    ),
                    random_id=cli.rnd_id() // 9000000000,
                )
            )

            await app.promote_chat_member(
                chat_id,
                assid,
                privileges=ChatAdminRights(
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

            await msg.edit_text("✅ Voice chat started successfully ⚡️")
        except Exception as e:
            await msg.edit_text(f"⚠️ Error: Give bot permission for video chat.\n{e}")


# ==========================
#  End Group Call
# ==========================
@app.on_message(filters.command(["vcend", "endvc"], ["/", "!"]))
async def stop_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant = await db.get_assistant(chat_id)

    if assistant is None:
        return await app.send_message(chat_id, "❌ Error: Assistant not found!")

    cli = getattr(assistant, "_client", None)
    if cli is None:
        return await app.send_message(chat_id, "❌ Assistant Pyrogram client missing!")

    ass_user = await cli.get_me()
    assid = ass_user.id

    msg = await app.send_message(chat_id, "🔇 Closing the voice chat...")

    try:
        group_call = await get_group_call(cli, m, err_msg=", voice chat already ended")
        if not group_call:
            return
        await cli.invoke(DiscardGroupCall(call=group_call))
        await msg.edit_text("✅ Voice chat closed successfully ⚡️")
    except Exception as e:
        if "GROUPCALL_FORBIDDEN" in str(e):
            try:
                await app.promote_chat_member(
                    chat_id,
                    assid,
                    privileges=ChatAdminRights(
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

                group_call = await get_group_call(cli, m, err_msg=", voice chat already ended")
                if not group_call:
                    return
                await cli.invoke(DiscardGroupCall(call=group_call))

                await app.promote_chat_member(
                    chat_id,
                    assid,
                    privileges=ChatAdminRights(
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

                await msg.edit_text("✅ Voice chat closed successfully ⚡️")
            except Exception as ex:
                await msg.edit_text(f"⚠️ Give bot full admin rights and try again!\n\n{ex}")
        else:
            await msg.edit_text(f"⚠️ Failed to close voice chat:\n{e}")
