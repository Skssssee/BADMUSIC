import asyncio
import aiohttp
import os
import re
import yt_dlp
from typing import Union
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType
from youtubesearchpython.future import VideosSearch
from BADMUSIC.utils.database import is_on_off
from BADMUSIC.utils.formatters import time_to_seconds
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        error_text = errorz.decode("utf-8").lower()
        if "unavailable videos are hidden" in error_text:
            return out.decode("utf-8")
        else:
            logger.error(f"Shell command error: {error_text}")
            return error_text
    return out.decode("utf-8")

async def get_stream_url(query, video=False):
    base_url = "http://18.136.212.47:5050/api/yt-audio-video"
    api_key = "3485e30bbdd3f9393b11bee473782b698051f5a863e9a53b82b5c770e9fafeed"

    async with aiohttp.ClientSession() as session:  
        payload = {  
            "url": query,  
            "quality": "720p" if video else "audio"  
        }  
        headers = {  
            "X-API-Key": api_key,  
            "Content-Type": "application/json"  
        }  
        try:
            async with session.post(base_url, json=payload, headers=headers) as response:  
                if response.status != 200:  
                    logger.error(f"Stream URL request failed with status {response.status}")
                    return ""  
                info = await response.json()  
                return info.get("video_stream_url" if video else "audio_stream_url", "")
        except Exception as e:
            logger.error(f"Error in get_stream_url: {str(e)}")
            return ""

class YouTubeAPI:
    def __init__(self):  # Fixed: Corrected `init` to `__init__`
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube.com|youtu.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if re.search(self.regex, link):  
            return True  
        return False  

    async def url(self, message_1: Message) -> Union[str, None]:  
        messages = [message_1]  
        if message_1.reply_to_message:  
            messages.append(message_1.reply_to_message)  
        text = ""  
        offset = None  
        length = None  
        for message in messages:  
            if offset:  
                break  
            if message.entities:  
                for entity in message.entities:  
                    if entity.type == MessageEntityType.URL:  
                        text = message.text or message.caption  
                        offset, length = entity.offset, entity.length  
                        break  
            elif message.caption_entities:  
                for entity in message.caption_entities:  
                    if entity.type == MessageEntityType.TEXT_LINK:  
                        return entity.url  
        if offset is None:  
            return None  
        return text[offset : offset + length]  

    async def details(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        results = VideosSearch(link, limit=1)  
        for result in (await results.next())["result"]:  
            title = result["title"]  
            duration_min = result["duration"]  
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]  
            vidid = result["id"]  
            duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))  
        return title, duration_min, duration_sec, thumbnail, vidid  

    async def title(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        results = VideosSearch(link, limit=1)  
        for result in (await results.next())["result"]:  
            title = result["title"]  
        return title  

    async def duration(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        results = VideosSearch(link, limit=1)  
        for result in (await results.next())["result"]:  
            duration = result["duration"]  
        return duration  

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        results = VideosSearch(link, limit=1)  
        for result in (await results.next())["result"]:  
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]  
        return thumbnail  

    async def video(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        return await get_stream_url(link, True)  

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.listbase + link  
        if "&" in link:  
            link = link.split("&")[0]  
        playlist = await shell_cmd(  
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"  
        )  
        try:  
            result = playlist.split("\n")  
            result = [key for key in result if key]  # Remove empty strings
        except Exception as e:  
            logger.error(f"Error in playlist: {str(e)}")
            result = []  
        return result  

    async def track(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        results = VideosSearch(link, limit=1)  
        for result in (await results.next())["result"]:  
            title = result["title"]  
            duration_min = result["duration"]  
            vidid = result["id"]  
            yturl = result["link"]  
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]  
        track_details = {  
            "title": title,  
            "link": yturl,  
            "vidid": vidid,  
            "duration_min": duration_min,  
            "thumb": thumbnail,  
        }  
        return track_details, vidid  

    async def formats(self, link: str, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        ytdl_opts = {"quiet": True}  
        ydl = yt_dlp.YoutubeDL(ytdl_opts)  
        formats_available = []  
        try:  
            r = ydl.extract_info(link, download=False)  
            for format in r["formats"]:  
                try:  
                    if "dash" not in str(format["format"]).lower():  
                        formats_available.append(  
                            {  
                                "format": format["format"],  
                                "filesize": format.get("filesize"),  
                                "format_id": format["format_id"],  
                                "ext": format["ext"],  
                                "format_note": format.get("format_note"),  
                                "yturl": link,  
                            }  
                        )  
                except Exception as e:  
                    logger.error(f"Error processing format: {str(e)}")
                    continue  
        except Exception as e:  
            logger.error(f"Error in formats: {str(e)}")
        return formats_available, link  

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  
        a = VideosSearch(link, limit=10)  
        result = (await a.next()).get("result")  
        title = result[query_type]["title"]  
        duration_min = result[query_type]["duration"]  
        vidid = result[query_type]["id"]  
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]  
        return title, duration_min, thumbnail, vidid  

    async def download(  
        self,  
        link: str,  
        mystic,  
        video: Union[bool, str] = None,  
        videoid: Union[bool, str] = None,  
        songaudio: Union[bool, str] = None,  
        songvideo: Union[bool, str] = None,  
        format_id: Union[bool, str] = None,  
        title: Union[bool, str] = None,  
    ) -> str:  
        if videoid:  
            link = self.base + link  
        if "&" in link:  
            link = link.split("&")[0]  

        async def download_from_url(url, filename):  
            async with aiohttp.ClientSession() as session:  
                try:  
                    async with session.get(url) as r:  
                        if r.status == 200:  
                            with open(filename, "wb") as f:  
                                while True:  
                                    chunk = await r.content.read(1024 * 64)  # 64KB chunks  
                                    if not chunk:  
                                        break  
                                    f.write(chunk)  
                            logger.info(f"Downloaded file: {filename}")
                            return filename  
                        else:  
                            logger.error(f"Failed to download from URL: {r.status}")
                            return None  
                except Exception as e:  
                    logger.error(f"Error downloading from URL: {str(e)}")
                    return None  

        def audio_dl():  
            ydl_optssx = {  
                "format": "bestaudio/best",  
                "outtmpl": "downloads/%(id)s.%(ext)s",  
                "geo_bypass": True,  
                "nocheckcertificate": True,  
                "quiet": True,  
                "no_warnings": True,  
            }  
            try:  
                x = yt_dlp.YoutubeDL(ydl_optssx)  
                info = x.extract_info(link, download=False)  
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")  
                if os.path.exists(xyz):  
                    logger.info(f"Using existing file: {xyz}")
                    return xyz  
                x.download([link])  
                logger.info(f"Downloaded audio: {xyz}")
                return xyz  
            except Exception as e:  
                logger.error(f"Error in audio_dl: {str(e)}")
                return None  

        def video_dl():  
            ydl_optssx = {  
                "format": "(bestvideo[height<=?720][ext=mp4])+bestaudio[ext=m4a]/best",  
                "outtmpl": "downloads/%(id)s.%(ext)s",  
                "geo_bypass": True,  
                "nocheckcertificate": True,  
                "quiet": True,  
                "no_warnings": True,  
                "merge_output_format": "mp4",  
                "postprocessors": [{  
                    "key": "FFmpegVideoConvertor",  
                    "preferedformat": "mp4",  
                }],  
            }  
            try:  
                x = yt_dlp.YoutubeDL(ydl_optssx)  
                info = x.extract_info(link, download=False)  
                xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")  
                if os.path.exists(xyz):  
                    logger.info(f"Using existing file: {xyz}")
                    return xyz  
                x.download([link])  
                logger.info(f"Downloaded video: {xyz}")
                return xyz  
            except Exception as e:  
                logger.error(f"Error in video_dl: {str(e)}")
                return None  

        def song_video_dl():  
            ydl_optssx = {  
                "format": f"(bestvideo[height<=?720][ext=mp4])+bestaudio[ext=m4a]/best",  
                "outtmpl": f"downloads/{title}.%(ext)s",  
                "geo_bypass": True,  
                "nocheckcertificate": True,  
                "quiet": True,  
                "no_warnings": True,  
                "merge_output_format": "mp4",  
                "postprocessors": [{  
                    "key": "FFmpegVideoConvertor",  
                    "preferedformat": "mp4",  # Ensure FFmpeg merges video and audio  
                }],  
            }  
            try:  
                x = yt_dlp.YoutubeDL(ydl_optssx)  
                x.download([link])  
                output_file = f"downloads/{title}.mp4"  
                logger.info(f"Downloaded song video: {output_file}")
                return output_file  
            except Exception as e:  
                logger.error(f"Error in song_video_dl: {str(e)}")
                return None  

        def song_audio_dl():  
            fpath = f"downloads/{title}.%(ext)s"  
            ydl_optssx = {  
                "format": format_id or "bestaudio/best",  
                "outtmpl": fpath,  
                "geo_bypass": True,  
                "nocheckcertificate": True,  
                "quiet": True,  
                "no_warnings": True,  
                "prefer_ffmpeg": True,  
                "postprocessors": [  
                    {  
                        "key": "FFmpegExtractAudio",  
                        "preferredcodec": "mp3",  
                        "preferredquality": "192",  
                    }  
                ],  
            }  
            try:  
                x = yt_dlp.YoutubeDL(ydl_optssx)  
                x.download([link])  
                output_file = f"downloads/{title}.mp3"  
                logger.info(f"Downloaded song audio: {output_file}")
                return output_file  
            except Exception as e:  
                logger.error(f"Error in song_audio_dl: {str(e)}")
                return None  

        loop = asyncio.get_running_loop()  
        if songvideo:  
            return await loop.run_in_executor(None, song_video_dl)  
        elif songaudio:  
            return await loop.run_in_executor(None, song_audio_dl)  
        elif video:  
            return await loop.run_in_executor(None, video_dl)  
        else:  
            stream_url = await get_stream_url(link, video)  
            if not stream_url:  
                logger.error("Stream URL not found, falling back to audio_dl")
                return await loop.run_in_executor(None, audio_dl), None  
            # Get title for filename  
            try:  
                results = VideosSearch(link, limit=1)  
                result = (await results.next())["result"][0]  
                title = re.sub(r'[^\w\s-]', '_', result["title"]).replace(" ", "_")  
            except Exception as e:  
                logger.error(f"Error fetching title for filename: {str(e)}")
                title = "downloaded_file"  
            filename = f"downloads/{title}.{'mp4' if video else 'mp3'}"  
            if not os.path.exists("downloads"):  
                os.makedirs("downloads")  
            downloaded_file = await download_from_url(stream_url, filename)  
            return downloaded_file, None