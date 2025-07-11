from pyrogram import Client
import config
from ..logging import LOGGER
assistants = []
assistantids = []
class Userbot(Client):
    def __init__(self):
        self.one = Client(
            name="BadAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=True,
        )
        self.two = Client(
            name="BadAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=True,
        )
        self.three = Client(
            name="BadAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=True,
        )
        self.four = Client(
            name="BadAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=True,
        )
        self.five = Client(
            name="BadAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=True,
        )
    async def start(self):
        LOGGER(__name__).info(f"❖ ꜱᴛᴀʀᴛɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛꜱ...")
        if config.STRING1:
            await self.one.start()
            try:
                await self.one.join_chat("PBX_CHAT")
                await self.one.join_chat("PBX_UPDATE")
            except:
                pass
            assistants.append(1)
            try:
                await self.one.send_message(config.LOGGER_ID, "❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ")
            except:
                LOGGER(__name__).error(
                    "❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ 1 ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ!"
                )
                exit()
            self.one.id = self.one.me.id
            self.one.name = self.one.me.mention
            self.one.username = self.one.me.username
            assistantids.append(self.one.id)
            LOGGER(__name__).info(f"❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ ᴀs ➥ {self.one.name}")
        if config.STRING2:
            await self.two.start()
            try:
                await self.two.join_chat("PBX_CHAT")
                await self.one.join_chat("PBX_UPDATE")
            except:
                pass
            assistants.append(2)
            try:
                await self.two.send_message(config.LOGGER_ID, "❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ")
            except:
                LOGGER(__name__).error(
                    "ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ 2 ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ!"
                )
                exit()
            self.two.id = self.two.me.id
            self.two.name = self.two.me.mention
            self.two.username = self.two.me.username
            assistantids.append(self.two.id)
            LOGGER(__name__).info(f"❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴡᴏ ꜱᴛᴀʀᴛᴇᴅ ᴀs ➥ {self.two.name}")
        if config.STRING3:
            await self.three.start()
            try:
                await self.three.join_chat("PBX_CHAT")
                await self.one.join_chat("PBX_UPDATE")
            except:
                pass
            assistants.append(3)
            try:
                await self.three.send_message(config.LOGGER_ID, "❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ")
            except:
                LOGGER(__name__).error(
                    "ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ 3 ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ! "
                )
                exit()
            self.three.id = self.three.me.id
            self.three.name = self.three.me.mention
            self.three.username = self.three.me.username
            assistantids.append(self.three.id)
            LOGGER(__name__).info(f"❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛʜʀᴇᴇ ꜱᴛᴀʀᴛᴇᴅ ᴀs ➥ {self.three.name}")
        if config.STRING4:
            await self.four.start()
            try:
                await self.four.join_chat("PBX_CHAT")
                await self.one.join_chat("PBX_UPDATE")
            except:
                pass
            assistants.append(4)
            try:
                await self.four.send_message(config.LOGGER_ID, "ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ")
            except:
                LOGGER(__name__).error(
                    "ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ 4 ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ! "
                )
                exit()
            self.four.id = self.four.me.id
            self.four.name = self.four.me.mention
            self.four.username = self.four.me.username
            assistantids.append(self.four.id)
            LOGGER(__name__).info(f"ᴀꜱꜱɪꜱᴛᴀɴᴛ ғᴏᴜʀᴇ ꜱᴛᴀʀᴛᴇᴅ ᴀs {self.four.name}")
        if config.STRING5:
            await self.five.start()
            try:
                await self.five.join_chat("PBX_CHAT")
                await self.one.join_chat("PBX_UPDATE")
            except:
                pass
            assistants.append(5)
            try:
                await self.five.send_message(config.LOGGER_ID, "ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜱᴛᴀʀᴛᴇᴅ")
            except:
                LOGGER(__name__).error(
                    "ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ 5 ʜᴀꜱ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴀᴄᴄᴇꜱꜱ ᴛʜᴇ ʟᴏɢ ɢʀᴏᴜᴘ. ᴍᴀᴋᴇ ꜱᴜʀᴇ ᴛʜᴀᴛ ʏᴏᴜ ʜᴀᴠᴇ ᴀᴅᴅᴇᴅ ʏᴏᴜʀ ᴀꜱꜱɪꜱᴛᴀɴᴛ ᴛᴏ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ ᴀɴᴅ ᴘʀᴏᴍᴏᴛᴇᴅ ᴀꜱ ᴀᴅᴍɪɴ! "
                )
                exit()
            self.five.id = self.five.me.id
            self.five.name = self.five.me.mention
            self.five.username = self.five.me.username
            assistantids.append(self.five.id)
            LOGGER(__name__).info(f"ᴀꜱꜱɪꜱᴛᴀɴᴛ ꜰɪᴠᴇ ꜱᴛᴀʀᴛᴇᴅ ᴀꜱ {self.five.name}")
    async def stop(self):
        LOGGER(__name__).info(f"❖ ꜱᴛᴏᴘᴘɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛꜱ...")
        try:
            if config.STRING1:
                await self.one.stop()
            if config.STRING2:
                await self.two.stop()
            if config.STRING3:
                await self.three.stop()
            if config.STRING4:
                await self.four.stop()
            if config.STRING5:
                await self.five.stop()
        except:
            pass
