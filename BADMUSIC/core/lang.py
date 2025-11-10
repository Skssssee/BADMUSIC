import json
from functools import wraps
from pathlib import Path

from BADMUSIC import db, logger

lang_codes = {
    "ar": "اَلْعَرَبِيَّةُ",
    "de": "ᴅᴇᴜᴛsᴄʜ",
    "en": "ᴇɴɢʟɪsʜ",
    "sm": "sᴍᴀʟʟᴄᴀᴘ",
    "es": "ᴇsᴘᴀñᴏʟ",
    "fr": "ғʀᴀɴçᴀɪs",
    "hi": "हिंदी",
    "ja": "にほんご",
    "my": "မြန်မာ",
    "pa": "ਪੰਜਾਬੀ",
    "pt": "ᴘᴏʀᴛᴜɢᴜês", 
    "ru": "ʀᴜᴄᴄᴋɪʏ",
    "zh": "中文",
}

class Language:

    def __init__(self):
        self.lang_codes = lang_codes
        self.lang_dir = Path("BADMUSIC/utils/lang")
        self.languages = self.load_files()

    def load_files(self):
        languages = {}
        lang_files = {file.stem: file for file in self.lang_dir.glob("*.json")}
        for lang_code, lang_file in lang_files.items():
            with open(lang_file, "r", encoding="utf-8") as file:
                languages[lang_code] = json.load(file)
        logger.info(f"❖ ʟᴏᴀᴅᴇᴅ ʟᴀɴɢᴜᴀɢᴇꜱ: {len(languages)} 🏁")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        lang_code = await db.get_lang(chat_id)
        return self.languages[lang_code]

    def get_languages(self) -> dict:
        files = {f.stem for f in self.lang_dir.glob("*.json")}
        return {code: self.lang_codes[code] for code in sorted(files)}

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                if hasattr(fallen, "chat"):
                    chat = fallen.chat
                elif hasattr(fallen, "message"):
                    chat = fallen.message.chat

                if chat.id in db.blacklisted:
                    return await chat.leave()

                lang_code = await db.get_lang(chat.id)
                lang_dict = self.languages[lang_code]

                setattr(fallen, "lang", lang_dict)
                return await func(*args, **kwargs)

            return wrapper

        return decorator
