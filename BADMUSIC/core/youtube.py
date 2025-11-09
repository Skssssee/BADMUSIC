import os
import re
import random
import asyncio
import aiohttp
import glob
import logging
from pathlib import Path
from typing import Optional, Union, Tuple
from urllib.parse import urlparse

import yt_dlp
from py_yt import VideosSearch
from pyrogram import enums, types

from BADMUSIC import config, logger
from BADMUSIC.utils import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.listbase = "https://youtube.com/playlist?list="
        self.regex = r"(https?://)?(www\.|m\.)?(youtube\.com/(watch\?v=|shorts/)|youtu\.be/)([a-zA-Z0-9_-]{11})"
        self.cookies = []
        self.checked = False
        self._cached_cookie = None
        self._info_cache = {}

    def get_cookies(self):
        if not self.checked:
            folder_path = os.path.join(os.getcwd(), "BADMUSIC/cookies")
            txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
            if txt_files:
                self.cookies = [os.path.basename(f) for f in txt_files]
            self.checked = True
        if not self.cookies:
            return None
        chosen_file = random.choice(self.cookies)
        log_filename = os.path.join(os.getcwd(), "BADMUSIC/cookies", "logs.csv")
        with open(log_filename, 'a') as file:
            file.write(f'Chosen File: {chosen_file}\n')
        self._cached_cookie = f"BADMUSIC/cookies/{chosen_file}"
        return self._cached_cookie

    def cookie_txt_file(self):
        if self._cached_cookie:
            return self._cached_cookie
        return self.get_cookies()

    def extract_video_info(self, link: str) -> dict:
        if link in self._info_cache:
            return self._info_cache[link]
        ytdl_opts = {
            "quiet": True,
            "cookiefile": self.cookie_txt_file(),
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
        self._info_cache[link] = info
        return info

    def parse_tg_link(self, link: str) -> Tuple[Optional[str], Optional[int]]:
        """Telegram link se chat username aur message ID extract karta hai"""
        parsed = urlparse(link)
        path = parsed.path.strip('/')
        parts = path.split('/')
        
        if len(parts) >= 2:
            return str(parts[0]), int(parts[1])
            
        return None, None

    async def fetch_song(self, query: str, streamtype: str) -> dict:
        api_url = config.API_URL
        vid = "true" if streamtype.lower() == "video" else "false"
        params = {"query": query, "vid": vid}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, params=params) as response:
                    data = await response.json()
                    return data
        except Exception as e:
            return {"error": str(e)}

    async def download_tg_media(self, tg_link: str) -> Optional[str]:
        from BADMUSIC import app
        c_username, message_id = self.parse_tg_link(tg_link)
        if not c_username or not message_id:
            return None

        if c_username.startswith("@"):
            c_username = c_username[1:]

        try:
            msg = await app.get_messages(c_username, message_id)
            if not msg or not msg.media:
                return None

            filex = msg.audio or msg.video or msg.document
            if not filex:
                return None

            if msg.audio:
                file_name = f"{filex.file_unique_id}.{filex.file_name.split('.')[-1] if filex.file_name else 'ogg'}"
            elif msg.video or msg.document:
                file_name = f"{filex.file_unique_id}.{filex.file_name.split('.')[-1] if filex.file_name else 'mp4'}"
            else:
                return None

            fname = os.path.join("downloads", file_name)
            if os.path.exists(fname):
                return fname

            await app.download_media(msg, fname)
            return fname

        except Exception as e:
            logging.error(f"ᴇʀʀᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛɢ ᴍᴇᴅɪᴀ: {e}")
            return None

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.URL:
                        return text[entity.offset : entity.offset + entity.length]

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == enums.MessageEntityType.TEXT_LINK:
                        return entity.url

        return None

    async def search(self, query: str, m_id: int, video: bool = False) -> Track | None:
        _search = VideosSearch(query, limit=1)
        results = await _search.next()
        if results and results["result"]:
            data = results["result"][0]
            return Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name"),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                message_id=m_id,
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails", [{}])[-1].get("url").split("?")[0],
                url=data.get("link"),
                view_count=data.get("viewCount", {}).get("short"),
                video=video,
            )
        return None

    async def details(self, link: str, videoid: Union[bool, str] = None) -> Tuple[str, str, int, str, str]:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        title = search_result["title"]
        duration_str = search_result["duration"]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        vidid = search_result["id"]
        duration_sec = int(utils.to_seconds(duration_str)) if duration_str else 0
        return title, duration_str, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["thumbnails"][0]["url"].split("?")[0]

    async def track(self, link: str, videoid: Union[bool, str] = None) -> Tuple[dict, str]:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        track_details = {
            "title": search_result["title"],
            "link": search_result["link"],
            "vidid": search_result["id"],
            "duration_min": search_result["duration"],
            "thumb": search_result["thumbnails"][0]["url"].split("?")[0],
        }
        return track_details, search_result["id"]

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None) -> Tuple[str, str, str, str]:
        if videoid:
            link = self.base + link
        if "?" in link:
            link = link.split("?")[0]
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=10)
        entries = (await results.next()).get("result")
        selected = entries[query_type]
        return selected["title"], selected["duration"], selected["thumbnails"][0]["url"].split("?")[0], selected["id"]

    async def get_download_link(self, query: str, video_stream: bool = False) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        streamtype = "video" if video_stream else "audio"
        song_data = await self.fetch_song(query, streamtype)

        if not song_data or "error" in song_data or "link" not in song_data:
            error_msg = song_data.get("error", "ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇꜱꜱ Qᴜᴇʀʏ")
            return None, None, error_msg

        song_url = song_data["link"]
        c_username, message_id = self.parse_tg_link(song_url)
        
        return c_username, message_id, None

    async def download(self, video_id: str, video: bool = False, title: Optional[str] = None) -> Optional[str]:
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        if config.API_ENABLED:
            query = title or (await self.title(video_id, True))
            streamtype = "video" if video else "audio"
            song_data = await self.fetch_song(query, streamtype)
            if song_data and "link" in song_data and not song_data.get("error"):
                tg_link = song_data["link"]
                if tg_link.startswith("https://t.me/"):
                    local_path = await self.download_tg_media(tg_link)
                    if local_path:
                        return local_path
                return tg_link 

        # Fallback to direct yt_dlp
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "ignoreerrors": True,
            "nocheckcertificate": True,
            "cookiefile": self.cookie_txt_file(),
        }

        if video:
            ydl_opts = {
                **base_opts,
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio)",
                "merge_output_format": "mp4",
            }
        else:
            ydl_opts = {
                **base_opts,
                "format": "bestaudio[ext=webm][acodec=opus]",
            }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return filename

        return await asyncio.to_thread(_download)
