import os
import re
import yt_dlp
import random
import asyncio
import aiohttp
from pathlib import Path
from typing import Optional, Union, Tuple
from urllib.parse import urlparse
import glob

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch

from BADMUSIC import app, config, logger
from BADMUSIC.utils import Track, utils


class YouTube:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.cookies = []
        self.checked = False
        self.warned = False
        self.regex = re.compile(
            r"(https?://)?(www\.|m\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

    def get_cookies(self):
        if not config.COOKIES_ENABLED:
            return None
        if not self.checked:
            folder_path = os.path.join(os.getcwd(), "BADMUSIC/cookies")
            txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
            if txt_files:
                self.cookies = [os.path.basename(f) for f in txt_files]
            self.checked = True
        if not self.cookies:
            if not self.warned:
                self.warned = True
                logger.warning("Cookies are missing; downloads might fail.")
            return None
        basename = random.choice(self.cookies)
        return f"BADMUSIC/cookies/{basename}"

    async def save_cookies(self, urls: list[str]) -> None:
        logger.info("Saving cookies from urls...")
        for url in urls:
            path = f"BADMUSIC/cookies/cookie{random.randint(10000, 99999)}.txt"
            link = url.replace("me/", "me/raw/")
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    with open(path, "wb") as fw:
                        fw.write(await resp.read())
        logger.info("Cookies saved.")

    async def fetch_song(self, query: str, streamtype: str) -> dict:
        if not config.API_ENABLED:
            return {"error": "API is disabled"}
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

    def parse_tg_link(self, link: str) -> Tuple[Optional[str], Optional[int]]:
        parsed = urlparse(link)
        path = parsed.path.strip('/')
        parts = path.split('/')
        
        if len(parts) >= 2:
            return str(parts[0]), int(parts[1])
            
        return None, None

    async def download_tg_media(self, tg_link: str) -> Optional[str]:
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
            logger.error(f"ᴇʀʀᴏʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴛɢ ᴍᴇᴅɪᴀ: {e}")
            return None

    async def get_download_link(self, query: str, video_stream: bool = False) -> Tuple[Optional[str], Optional[int], Optional[str]]:
        if not config.API_ENABLED:
            return None, None, "API is disabled"
        streamtype = "video" if video_stream else "audio"
        song_data = await self.fetch_song(query, streamtype)

        if not song_data or "error" in song_data or "link" not in song_data:
            error_msg = song_data.get("error", "ꜰᴀɪʟᴇᴅ ᴛᴏ ᴘʀᴏᴄᴇꜱꜱ Qᴜᴇʀʏ")
            return None, None, error_msg

        song_url = song_data["link"]
        c_username, message_id = self.parse_tg_link(song_url)
        
        return c_username, message_id, None

    async def title(self, link: str, videoid: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        return (await results.next())["result"][0]["title"]

    def valid(self, url: str) -> bool:
        return bool(re.match(self.regex, url))

    def url(self, message_1: types.Message) -> Union[str, None]:
        messages = [message_1]
        link = None
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)

        for message in messages:
            text = message.text or message.caption or ""

            if message.entities:
                for entity in message.entities:
                    if entity.type == enums.MessageEntityType.URL:
                        link = text[entity.offset : entity.offset + entity.length]
                        break

            if message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == enums.MessageEntityType.TEXT_LINK:
                        link = entity.url
                        break

        if link:
            return link.split("&si")[0]
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

    async def playlist(self, limit: int, user: str, url: str, video: bool) -> list[Track]:
        plist = await Playlist.get(url)
        tracks = []
        for data in plist["videos"][:limit]:
            track = Track(
                id=data.get("id"),
                channel_name=data.get("channel", {}).get("name", ""),
                duration=data.get("duration"),
                duration_sec=utils.to_seconds(data.get("duration")),
                title=data.get("title")[:25],
                thumbnail=data.get("thumbnails")[-1].get("url").split("?")[0],
                url=data.get("link").split("&list=")[0],
                user=user,
                view_count="",
                video=video,
            )
            tracks.append(track)
        return tracks

    async def download(self, video_id: str, video: bool = False, title: Optional[str] = None) -> Optional[str]:
        url = self.base + video_id
        ext = "mp4" if video else "webm"
        filename = f"downloads/{video_id}.{ext}"

        if Path(filename).exists():
            return filename

        local_path = None
        if config.API_ENABLED:
            query = title or (await self.title(video_id, True))
            streamtype = "video" if video else "audio"
            song_data = await self.fetch_song(query, streamtype)
            if song_data and "link" in song_data and not song_data.get("error"):
                tg_link = song_data["link"]
                if tg_link.startswith("https://t.me/"):
                    local_path = await self.download_tg_media(tg_link)
                else:
                    return tg_link  # Direct stream URL if not TG

        if local_path:
            return local_path

        # Fallback to direct yt_dlp
        cookie = self.get_cookies()
        base_opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "quiet": True,
            "noplaylist": True,
            "geo_bypass": True,
            "no_warnings": True,
            "overwrites": False,
            "ignoreerrors": True,
            "nocheckcertificate": True,
            "cookiefile": cookie,
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
                try:
                    ydl.download([url])
                except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError):
                    if cookie:
                        basename = cookie.split("/")[-1]
                        if basename in self.cookies:
                            self.cookies.remove(basename)
                    return None
                except Exception as ex:
                    logger.error(f"ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ: {ex}")
                    return None
            return filename

        res = await asyncio.to_thread(_download)
        return res
