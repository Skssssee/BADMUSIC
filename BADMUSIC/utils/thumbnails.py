import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from youtubesearchpython.__future__ import VideosSearch

from BADMUSIC import config
from BADMUSIC.utils import Track


# Constants
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

PANEL_W, PANEL_H = 763, 545
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 88
TRANSPARENCY = 170
INNER_OFFSET = 36

THUMB_W, THUMB_H = 542, 273
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + INNER_OFFSET

TITLE_X = 377
META_X = 377
TITLE_Y = THUMB_Y + THUMB_H + 10
META_Y = TITLE_Y + 45

BAR_X, BAR_Y = 388, META_Y + 45
BAR_RED_LEN = 280
BAR_TOTAL_LEN = 480

ICONS_W, ICONS_H = 415, 45
ICONS_X = PANEL_X + (PANEL_W - ICONS_W) // 2
ICONS_Y = BAR_Y + 48

MAX_TITLE_WIDTH = 580


class Thumbnail:
    def __init__(self):
        try:
            self.title_font = ImageFont.truetype("BADMUSIC/utils/resources/fonts/font2.ttf", 32)
            self.regular_font = ImageFont.truetype("BADMUSIC/utils/resources/fonts/font.ttf", 18)
        except OSError:
            self.title_font = self.regular_font = ImageFont.load_default()

    def trim_to_width(self, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> str:
        ellipsis = "…"
        if font.getlength(text) <= max_w:
            return text
        for i in range(len(text) - 1, 0, -1):
            if font.getlength(text[:i] + ellipsis) <= max_w:
                return text[:i] + ellipsis
        return ellipsis

    async def save_thumb(self, output_path: str, url: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(output_path, "wb") as f:
                        await f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            cache_path = os.path.join(CACHE_DIR, f"{song.id}_v4.png")
            if os.path.exists(cache_path):
                return cache_path

            temp = os.path.join(CACHE_DIR, f"temp_{song.id}.jpg")
            thumb_path = os.path.join(CACHE_DIR, f"thumb{song.id}.png")

            await self.save_thumb(thumb_path, song.thumbnail)

            # Determine if live (basic check, as duration might be None or 'Live')
            duration = song.duration or ""
            is_live = not duration or str(duration).strip().lower() in {"", "live", "live now"}
            duration_text = "Live" if is_live else duration or "Unknown Mins"

            title = re.sub(r"\W+", " ", song.title or "Unsupported Title").title()
            views = song.view_count or "Unknown Views"
            thumbnail = song.thumbnail

            # Create base image
            base = Image.open(thumb_path).resize(size).convert("RGBA")
            bg = ImageEnhance.Brightness(base.filter(ImageFilter.BoxBlur(10))).enhance(0.6)

            # Frosted glass panel
            panel_area = bg.crop((PANEL_X, PANEL_Y, PANEL_X + PANEL_W, PANEL_Y + PANEL_H))
            overlay = Image.new("RGBA", (PANEL_W, PANEL_H), (255, 255, 255, TRANSPARENCY))
            frosted = Image.alpha_composite(panel_area, overlay)
            mask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(mask).rounded_rectangle((0, 0, PANEL_W, PANEL_H), 50, fill=255)
            bg.paste(frosted, (PANEL_X, PANEL_Y), mask)

            # Thumbnail image with rounded corners
            thumb = base.resize((THUMB_W, THUMB_H))
            tmask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(tmask).rounded_rectangle((0, 0, THUMB_W, THUMB_H), 20, fill=255)
            thumb.putalpha(tmask)
            bg.paste(thumb, (THUMB_X, THUMB_Y), thumb)

            # Draw details
            draw = ImageDraw.Draw(bg)
            trimmed_title = self.trim_to_width(title, self.title_font, MAX_TITLE_WIDTH)
            draw.text((TITLE_X, TITLE_Y), trimmed_title, fill="black", font=self.title_font)
            draw.text((META_X, META_Y), f"YouTube | {views}", fill="black", font=self.regular_font)

            # Progress bar
            draw.line([(BAR_X, BAR_Y), (BAR_X + BAR_RED_LEN, BAR_Y)], fill="red", width=6)
            draw.line([(BAR_X + BAR_RED_LEN, BAR_Y), (BAR_X + BAR_TOTAL_LEN, BAR_Y)], fill="gray", width=5)
            draw.ellipse([(BAR_X + BAR_RED_LEN - 7, BAR_Y - 7), (BAR_X + BAR_RED_LEN + 7, BAR_Y + 7)], fill="red")

            draw.text((BAR_X, BAR_Y + 15), "00:00", fill="black", font=self.regular_font)
            end_text = "Live" if is_live else duration_text
            end_x = BAR_X + BAR_TOTAL_LEN - (90 if is_live else 60)
            draw.text((end_x, BAR_Y + 15), end_text, fill="red" if is_live else "black", font=self.regular_font)

            # Icons (assuming path exists)
            icons_path = "BADMUSIC/utils/resources/images/play_icons.png"  
            if os.path.isfile(icons_path):
                ic = Image.open(icons_path).resize((ICONS_W, ICONS_H)).convert("RGBA")
                r, g, b, a = ic.split()
                black_ic = Image.merge("RGBA", (r.point(lambda *_: 0), g.point(lambda *_: 0), b.point(lambda *_: 0), a))
                bg.paste(black_ic, (ICONS_X, ICONS_Y), black_ic)

            # Cleanup temp files
            try:
                os.remove(thumb_path)
                os.remove(temp)  # If temp was created
            except OSError:
                pass

            bg.save(cache_path)
            return cache_path
        except Exception:
            return config.DEFAULT_THUMB
