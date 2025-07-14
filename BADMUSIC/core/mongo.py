from motor.motor_asyncio import AsyncIOMotorClient as _mongo_client_
from pymongo import MongoClient
from Badmunda import Client
import config
from ..logging import LOGGER

# Public MongoDB URL (consider keeping credentials secure in real applications)
TEMP_MONGODB = "mongodb+srv://BADMUNDA:BADMYDAD@badhacker.i5nw9na.mongodb.net/"

try:
    # Check if a custom MongoDB URI is provided in the config
    if config.MONGO_DB_URI is None:
        LOGGER(__name__).warning(
            "ɴᴏ ᴍᴏɴɢᴏᴅʙ ꜰᴏᴜɴᴅ, ᴅᴇꜰᴀᴜʟᴛɪɴɢ ᴛᴏ ᴘᴜʙʟɪᴄ ᴍᴏɴɢᴏᴅʙ...💚"
        )

        # Initialize a temporary Pyrogram client to retrieve bot's username
        with Client(
            "EraVibes",
            bot_token=config.BOT_TOKEN,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
        ) as temp_client:
            info = temp_client.get_me()
            username = info.username

        # Connect to MongoDB with the bot's username as the database name
        _mongo_async_ = _mongo_client_(TEMP_MONGODB)
        _mongo_sync_ = MongoClient(TEMP_MONGODB)
        mongodb = _mongo_async_[username]
        pymongodb = _mongo_sync_[username]

        LOGGER(__name__).info(f"ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ᴘᴜʙʟɪᴄ ᴍᴏɴɢᴏᴅʙ ᴡɪᴛʜ ᴜꜱᴇʀɴᴀᴍᴇ: {username}...💛")

    else:
        LOGGER(__name__).info("✦ ᴄᴏɴɴᴇᴄᴛɪɴɢ ᴛᴏ ʏᴏᴜʀ ᴄᴜꜱᴛᴏᴍ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ...💛")

        # Use custom MongoDB URI from config
        _mongo_async_ = _mongo_client_(config.MONGO_DB_URI)
        _mongo_sync_ = MongoClient(config.MONGO_DB_URI)
        mongodb = _mongo_async_.ERAVIBES
        pymongodb = _mongo_sync_.ERAVIBES

        LOGGER(__name__).info("✦ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ...❤️")

except Exception as e:
    # Log any exceptions that occur during connection
    LOGGER(__name__).error(f"✦ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ: {str(e)}...💚")
    exit()
