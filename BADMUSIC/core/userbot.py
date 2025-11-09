from pyrogram import Client

from BADMUSIC import config, logger


class Userbot(Client):
    def __init__(self):
        self.clients = []
        clients = {"one": "SESSION1", "two": "SESSION2", "three": "SESSION3"}
        for key, string_key in clients.items():
            name = f"BADMUSICUB{key[-1]}"
            session = getattr(config, string_key)
            setattr(
                self,
                key,
                Client(
                    name=name,
                    api_id=config.API_ID,
                    api_hash=config.API_HASH,
                    session_string=session,
                ),
            )

    async def boot_client(self, num: int, ub: Client):
        clients = {
            1: self.one,
            2: self.two,
            3: self.three,
        }
        client = clients[num]
        await client.start()
        client.id = client.me.id
        client.name = client.me.first_name
        client.username = client.me.username
        client.mention = client.me.mention
        self.clients.append(client)
        try:
            await client.send_message(
                config.LOGGER_ID,
                f"❖<b> {client.mention} ᴀꜱꜱɪꜱᴛᴀɴᴛ {num} sᴛᴀʀᴛᴇᴅ</b>\n\n● ɪᴅ ➥ <code>{client.id}</code>\n● ɴᴀᴍᴇ ➥ {client.name}\n● ᴜsᴇʀɴᴀᴍᴇ ➥ @{client.username}",
            )
        except:
            raise SystemExit(f"❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ {num} ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ ᴍᴇꜱꜱᴀɢᴇ ɪɴ ʟᴏɢ ɢʀᴏᴜᴘ😥")

        try:
            await client.join_chat("PBX_CHAT")
            await client.join_chat("PBX_UPDATE")
        except:
            pass
        logger.info(f"❖ ᴀꜱꜱɪꜱᴛᴀɴᴛ {num} ꜱᴛᴀʀᴛᴇᴅ ᴀꜱ @{client.username}")

    async def boot(self):
        if config.SESSION1:
            await self.boot_client(1, self.one)
        if config.SESSION2:
            await self.boot_client(2, self.two)
        if config.SESSION3:
            await self.boot_client(3, self.three)

    async def exit(self):
        if config.SESSION1:
            await self.one.stop()
        if config.SESSION2:
            await self.two.stop()
        if config.SESSION3:
            await self.three.stop()
        logger.info("❖ ꜱᴛᴏᴘᴘɪɴɢ ᴀꜱꜱɪꜱᴛᴀɴᴛꜱ 😥")
