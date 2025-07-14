from Badmunda import filters
from Badmunda.types import Message

from BADMUSIC import app
from BADMUSIC.core.call import Bad
from BADMUSIC.utils.database import is_Music_playing, music_off
from BADMUSIC.utils.decorators import AdminRightsCheck
from BADMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(filters.command(["pause", "cpause"]) & filters.group & ~BANNED_USERS)
@AdminRightsCheck
async def pause_admin(cli, message: Message, _, chat_id):
    if not await is_Music_playing(chat_id):
        return await message.reply_text(_["admin_1"])
    await music_off(chat_id)
    await Bad.pause_stream(chat_id)
    await message.reply_text(
        _["admin_2"].format(message.from_user.mention), reply_markup=close_markup(_)
    )
