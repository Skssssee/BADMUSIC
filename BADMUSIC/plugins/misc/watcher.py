from Badmunda import filters
from Badmunda.types import Message

from BADMUSIC import app
from BADMUSIC.core.call import Bad

welcome = 20
close = 30


@app.on_message(filters.video_chat_started, group=welcome)
@app.on_message(filters.video_chat_ended, group=close)
async def welcome(_, message: Message):
    await Bad.stop_stream_force(message.chat.id)
