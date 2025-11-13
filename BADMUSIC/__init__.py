import tim
import logging
from logging.handlers import RotatingFileHandler

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=10485760, backupCount=5),
        logging.StreamHandler(),
    ],
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("ntgcalls").setLevel(logging.CRITICAL)
logging.getLogger("pymongo").setLevel(logging.ERROR)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("pytgcalls").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


__version__ = "3.0"

from config import Config

config = Config()
config.check()
tasks = []
boot = time.time()

from BADMUSIC.core.bot import Bot
app = Bot()

from BADMUSIC.core.dir import ensure_dirs
ensure_dirs()

from BADMUSIC.core.userbot import Userbot
userbot = Userbot()

from BADMUSIC.core.mongo import MongoDB
db = MongoDB()

from BADMUSIC.core.lang import Language
lang = Language()

from BADMUSIC.core.telegram import Telegram
from BADMUSIC.core.youtube import YouTube
tg = Telegram()
yt = YouTube()

from BADMUSIC.utils import Queue
queue = Queue()

from BADMUSIC.core.calls import TgCall
Bad = TgCall()


async def stop() -> None:
    logger.info("❖ ꜱᴛᴏᴘᴘɪɴɢ...🪄")
    for task in tasks:
        task.cancel()
        try:
            await task
        except:
            pass

    await app.exit()
    await userbot.exit()
    await db.close()

    logger.info("❖ ꜱᴛᴏᴘᴘᴇᴅ.... 🍃\n")
