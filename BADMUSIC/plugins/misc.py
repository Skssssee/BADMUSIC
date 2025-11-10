import asyncio
import time
from typing import List

from pyrogram import enums, filters, types

from BADMUSIC import Bad, app, config, db, lang, queue, tasks, userbot, yt
from BADMUSIC.utils import buttons


@app.on_message(filters.video_chat_started, group=19)
@app.on_message(filters.video_chat_ended, group=20)
async def _watcher_vc(_, m: types.Message):
    await Bad.stop(m.chat.id)


async def auto_leave():
    while True:
        await asyncio.sleep(1800)
        for ub in userbot.clients:
            left = 0
            try:
                # handle async generator or coroutine for get_dialogs
                try:
                    dialogs = []
                    async for d in ub.get_dialogs():
                        dialogs.append(d)
                except TypeError:
                    # some versions return a list/coroutine
                    dialogs = await ub.get_dialogs()

                for dialog in dialogs:
                    chat_id = dialog.chat.id
                    if left >= 20:
                        break
                    if chat_id in [app.logger, -1002056907061]:
                        continue
                    if dialog.chat.type in [
                        enums.ChatType.GROUP,
                        enums.ChatType.SUPERGROUP,
                    ]:
                        if chat_id in db.active_calls:
                            continue
                        await ub.leave_chat(chat_id)
                        left += 1
                    await asyncio.sleep(5)
            except Exception:
                continue


async def track_time():
    while True:
        await asyncio.sleep(1)
        for chat_id in db.active_calls:
            if not await db.playing(chat_id):
                continue
            media = queue.get_current(chat_id)
            if not media.playing:
                continue
            media.time += 1
            if media.duration_sec and media.time >= media.duration_sec:
                # song ended
                try:
                    await app.send_message(chat_id, "🎧 ꜱᴏɴɢ ʜᴀꜱ ᴇɴᴅᴇᴅ ɪɴ ᴠᴄ 🥺")
                except Exception:
                    pass


async def update_timer(length=10):
    while True:
        await asyncio.sleep(7)
        for chat_id in db.active_calls:
            if not await db.playing(chat_id):
                continue
            try:
                media = queue.get_current(chat_id)
                duration, message_id = media.duration_sec, media.message_id
                if not duration or not message_id or not media.playing:
                    continue
                played = media.time
                remaining = duration - played
                pos = min(int((played / duration) * length), length - 1)
                timer = "—" * pos + "◉" + "—" * (length - pos - 1)

                if remaining <= 30:
                    nxt = queue.get_next(chat_id, check=True)
                    if nxt and not nxt.file_path:
                        try:
                            nxt.file_path = await yt.download(nxt.id, video=nxt.video)
                        except Exception:
                            pass

                if remaining < 10:
                    remove = True
                else:
                    remove = False
                    timer = f"{time.strftime('%M:%S', time.gmtime(played))} | {timer} | -{time.strftime('%M:%S', time.gmtime(remaining))}"

                await app.edit_message_reply_markup(
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=buttons.controls(chat_id=chat_id, timer=timer, remove=remove),
                )
            except Exception:
                pass


async def vc_watcher(sleep=15):
    while True:
        await asyncio.sleep(sleep)
        for chat_id in db.active_calls:
            try:
                client = await db.get_assistant(chat_id)
                played = await client.time(chat_id)
                participants = await client.get_participants(chat_id)
                if len(participants) < 2 and played > 30:
                    _lang = await lang.get_lang(chat_id)
                    sent = await app.edit_message_reply_markup(
                        chat_id=chat_id,
                        message_id=queue.get_current(chat_id).message_id,
                        reply_markup=buttons.controls(chat_id=chat_id, status=_lang["stopped"], remove=True),
                    )
                    await Bad.stop(chat_id)
                    await sent.reply_text(_lang["auto_left"])
            except Exception:
                continue


# ---------- Helper to safely fetch participants (handles async-generator or coroutine) ----------
async def fetch_participants_safe(client, chat_id) -> List:
    """
    Return list of participants for chat_id using client.
    Handles Pyrogram versions that return async generator vs coroutine.
    """
    participants = []
    try:
        # try async iteration first (some Pyrogram return async generator)
        async for p in client.get_participants(chat_id):
            participants.append(p)
    except TypeError:
        # fallback: get_participants returned coroutine/list
        try:
            res = await client.get_participants(chat_id)
            # res might be list-like or object; try to normalize
            if isinstance(res, list):
                participants = res
            else:
                # sometimes returns 'users' + 'chats' structure or phone.GroupParticipants
                # try to extract users
                users = getattr(res, "users", None)
                if users:
                    participants = users
                else:
                    # last resort, try to iterate
                    try:
                        for u in res:
                            participants.append(u)
                    except Exception:
                        participants = []
        except Exception:
            participants = []
    except Exception:
        # any other unexpected error
        participants = []

    return participants


# ---------- VC activity tracker that works even if assistant not joined to VC ----------
async def vc_activity_tracker(sleep=8):
    """
    Poll all groups where bot/assistant is present and try to detect
    voice-chat participant changes.

    Requirements:
      - bot (app) and at least one assistant userbot must be a member of the group.
      - This is polling-based (every `sleep` seconds).
    """
    last_participants = {}

    while True:
        await asyncio.sleep(sleep)
        for ub in userbot.clients:
            try:
                # collect dialogs safely (async generator OR coroutine)
                dialogs = []
                try:
                    async for d in ub.get_dialogs():
                        dialogs.append(d)
                except TypeError:
                    # fallback if get_dialogs returns coroutine/list
                    dialogs = await ub.get_dialogs()

                for dialog in dialogs:
                    try:
                        if dialog.chat.type not in (enums.ChatType.GROUP, enums.ChatType.SUPERGROUP):
                            continue

                        chat_id = dialog.chat.id

                        # fetch participants in a safe, version-tolerant way
                        participants = await fetch_participants_safe(ub, chat_id)

                        # if no participants info, skip
                        if not participants:
                            continue

                        # normalize getting user ids from participant entries:
                        current_ids = set()
                        for p in participants:
                            # different shapes: raw User, GroupCallParticipant, ChannelParticipant, etc.
                            uid = None
                            if hasattr(p, "user_id"):  # e.g. GroupCallParticipant has user_id
                                uid = getattr(p, "user_id", None)
                            elif hasattr(p, "user"):  # some objects wrap user
                                u = getattr(p, "user")
                                uid = getattr(u, "id", None)
                            elif hasattr(p, "id"):
                                uid = getattr(p, "id", None)
                            if uid:
                                current_ids.add(uid)

                        # If current_ids is empty, skip
                        if not current_ids:
                            continue

                        # ignore assistant's own id if present (we don't announce bot/assistant)
                        try:
                            me = await ub.get_me()
                            if me and me.id in current_ids:
                                current_ids.discard(me.id)
                        except Exception:
                            pass

                        old_ids = last_participants.get(chat_id, set())
                        joined = current_ids - old_ids
                        left = old_ids - current_ids

                        # send notifications (rate-limit a bit)
                        for user_id in joined:
                            try:
                                user = await app.get_users(user_id)
                                username = f"@{user.username}" if getattr(user, "username", None) else "(no username)"
                                text = (
                                    f"❖ ᴊᴏɪɴ ᴠᴄ\n\n"
                                    f"● ɪᴅ ➥ {user.id} \n"
                                    f"● ɴᴀᴍᴇ ➥ {getattr(user, 'first_name', '(no name)')} \n"
                                    f"● ᴜsᴇʀɴᴀᴍᴇ ➥ {username}"
                                )
                                await app.send_message(chat_id, text)
                                await asyncio.sleep(0.8)  # small pause to avoid flood-limit
                            except Exception:
                                continue

                        for user_id in left:
                            try:
                                user = await app.get_users(user_id)
                                username = f"@{user.username}" if getattr(user, "username", None) else "(no username)"
                                text = (
                                    f"❖ ʟᴇᴀᴠᴇ ᴠᴄ\n\n"
                                    f"● ɪᴅ ➥ {user.id} \n"
                                    f"● ɴᴀᴍᴇ ➥ {getattr(user, 'first_name', '(no name)')} \n"
                                    f"● ᴜsᴇʀɴᴀᴍᴇ ➥ {username}"
                                )
                                await app.send_message(chat_id, text)
                                await asyncio.sleep(0.8)
                            except Exception:
                                continue

                        # update last seen participants for this chat
                        last_participants[chat_id] = current_ids

                    except Exception as inner_e:
                        # better debugging info per chat
                        print(f"[VC_TRACK][chat {getattr(dialog.chat,'id', '?')}] {inner_e}")
                        continue

            except Exception as e:
                print(f"[VC_TRACK][client loop] {e}")
                continue


# ✅ Task registrations
if config.AUTO_LEAVE:
    tasks.append(asyncio.create_task(auto_leave()))

tasks.append(asyncio.create_task(track_time()))
tasks.append(asyncio.create_task(update_timer()))
tasks.append(asyncio.create_task(vc_watcher()))
tasks.append(asyncio.create_task(vc_activity_tracker()))
