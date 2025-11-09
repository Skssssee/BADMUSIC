from pathlib import Path

from BADMUSIC import logger


def ensure_dirs():
    for dir in ["cache", "downloads"]:
        Path(dir).mkdir(parents=True, exist_ok=True)
    logger.info("❖ ᴄᴀᴄʜᴇ ᴅɪʀᴇᴄᴛᴏʀɪᴇꜱ ᴜᴘᴅᴀᴛᴇᴅ 🌪️")
  
