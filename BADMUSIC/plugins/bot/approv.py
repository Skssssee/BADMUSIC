from BADMUSIC import app
from BADMUSIC.utils.database import get_assistant
from Badmunda import filters
from Badmunda.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from os import environ

EVAA = [
    [InlineKeyboardButton(text="• ᴧᴅᴅ мᴇ ʙᴧʙʏ •", url="https://t.me/PBX_CHAT")]
]

chat_id_env = environ.get("CHAT_ID")
CHAT_ID = [int(x) for x in chat_id_env.split(",")] if chat_id_env else []

TEXT = environ.get("APPROVED_WELCOME_TEXT", "❖ ʜᴇʟʟᴏ ʙᴀʙʏ ➥ {mention}\n\n❖ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ➥ {title}\n\n")
APPROVED = environ.get("APPROVED_WELCOME", "on").lower()

# Handle new join requests
@app.on_chat_join_request((filters.group | filters.channel) & filters.chat(CHAT_ID) if CHAT_ID else (filters.group | filters.channel))
async def autoapprove(client, message: ChatJoinRequest):
    chat = message.chat
    user = message.from_user
    print(f"๏ {user.first_name} ᴊᴏɪɴᴇᴅ 🤝")
    await client.approve_chat_join_request(chat.id, user.id)
    if APPROVED == "on":
        await client.send_message(
            chat_id=chat.id,
            text=TEXT.format(mention=user.mention, title=chat.title),
            reply_markup=InlineKeyboardMarkup(EVAA),
        )

# Command to accept old pending requests manually
@app.on_message(filters.command("allac") & filters.user(7588172591))  # Replace YOUR_ID
async def accept_old_requests(_, message):
    for chat_id in CHAT_ID:
        assistant = await get_assistant(chat_id)
        if not assistant:
            await message.reply_text(f"No assistant found for chat ID: {chat_id}")
            continue

        try:
            count = 0
            async for req in assistant.get_chat_join_requests(chat_id):
                await assistant.approve_chat_join_request(chat_id, req.from_user.id)
                count += 1
                if APPROVED == "on":
                    await assistant.send_message(
                        chat_id,
                        text=TEXT.format(mention=req.from_user.mention, title=req.chat.title),
                        reply_markup=InlineKeyboardMarkup(EVAA),
                    )
            await message.reply_text(f"Approved {count} old join requests in {chat_id}.")
        except Exception as e:
            await message.reply_text(f"Error in {chat_id}: {e}")
