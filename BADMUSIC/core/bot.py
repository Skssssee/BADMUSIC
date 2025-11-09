import pyrogram

from BADMUSIC import config, logger


class Bot(pyrogram.Client):
    def __init__(self):
        super().__init__(
            name="BADMUSIC",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            parse_mode=pyrogram.enums.ParseMode.HTML,
            max_concurrent_transmissions=7,
            link_preview_options=pyrogram.types.LinkPreviewOptions(is_disabled=True),
        )
        self.owner = config.OWNER_ID
        self.logger = config.LOGGER_ID
        self.bl_users = pyrogram.filters.user()
        self.sudoers = pyrogram.filters.user(self.owner)

    async def boot(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(self.logger, "❖<b> {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n● ɪᴅ ➥ <code>{self.id}</code>\n● ɴᴀᴍᴇ ➥ {self.name}\n● ᴜsᴇʀɴᴀᴍᴇ ➥ @{self.username}",
            )
            get = await self.get_chat_member(self.logger, self.id)
        except Exception as ex:
            raise SystemExit(f"❖ ʙᴏᴛ ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n● ʀᴇᴀꜱᴏɴ ➥ {self.logger}\n {ex}")

        if get.status != pyrogram.enums.ChatMemberStatus.ADMINISTRATOR:
            raise SystemExit("❖ ʙᴏᴛ ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.")
        logger.info(f"❖ ʙᴀᴅ ᴍᴜꜱɪᴄ ʙᴏᴛ ꜱᴛᴀʀᴛᴇᴅ ᴀꜱ ➥ {self.name} ...♥")

    async def exit(self):
        await super().stop()
        logger.info("❖ ʙᴏᴛ ꜱᴛᴏᴘᴘᴇᴅ 😥")
      
