from random import randint
from time import time

from pymongo import AsyncMongoClient
from bson import ObjectId

from BADMUSIC import config, logger, userbot


class MongoDB:
    def __init__(self):
        """
        Initialize the MongoDB connection.
        """
        self.mongo = AsyncMongoClient(config.MONGO_URL, serverSelectionTimeoutMS=12500)
        self.db = self.mongo.Bad

        self.admin_list = {}
        self.active_calls = {}
        self.blacklisted = []
        self.notified = []
        self.cache = self.db.cache
        self.logger = False

        self.assistant = {}
        self.assistantdb = self.db.assistant

        self.auth = {}
        self.authdb = self.db.auth

        self.chats = []
        self.chatsdb = self.db.chats

        self.lang = {}
        self.langdb = self.db.lang

        self.play_mode = []
        self.playmodedb = self.db.play

        self.users = []
        self.usersdb = self.db.users

    async def connect(self) -> None:
        """Check if we can connect to the database.

        Raises:
            SystemExit: If the connection to the database fails.
        """
        try:
            start = time()
            await self.mongo.admin.command("ping")
            logger.info(f"❖ ᴄᴏɴɴᴇᴄᴛᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ...🃏 ({time() - start:.2f}s)")
            await self.load_cache()
        except Exception as e:
            raise SystemExit(f"❖ ꜰᴀɪʟᴇᴅ ᴛᴏ ᴄᴏɴɴᴇᴄᴛ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ: {type(e).__name__}🥲") from e

    async def close(self) -> None:
        """Close the connection to the database."""
        await self.mongo.close()
        logger.info("❖ ᴄʟᴏꜱᴇᴅ ᴛᴏ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀꜱᴇ...🍃")

    # CACHE
    async def get_call(self, chat_id: int) -> bool:
        return chat_id in self.active_calls

    async def add_call(self, chat_id: int) -> None:
        self.active_calls[chat_id] = 1

    async def remove_call(self, chat_id: int) -> None:
        self.active_calls.pop(chat_id, None)

    async def playing(self, chat_id: int, paused: bool = None) -> bool | None:
        if paused is not None:
            self.active_calls[chat_id] = int(not paused)
        return bool(self.active_calls[chat_id])

    async def get_admins(self, chat_id: int, reload: bool = False) -> list[int]:
        from BADMUSIC.utils.admins import reload_admins

        if chat_id not in self.admin_list or reload:
            self.admin_list[chat_id] = await reload_admins(chat_id)
        return self.admin_list[chat_id]

    # AUTH METHODS
    async def _get_auth(self, chat_id: int) -> set[int]:
        if chat_id not in self.auth:
            doc = await self.authdb.find_one({"_id": chat_id})
            if not doc:
                doc = await self.authdb.find_one({"chat_id": chat_id})
            self.auth[chat_id] = set(doc.get("user_ids", []))
        return self.auth[chat_id]

    async def is_auth(self, chat_id: int, user_id: int) -> bool:
        return user_id in await self._get_auth(chat_id)

    async def add_auth(self, chat_id: int, user_id: int) -> None:
        users = await self._get_auth(chat_id)
        if user_id not in users:
            users.add(user_id)
            await self.authdb.update_one(
                {"_id": chat_id}, {"$addToSet": {"user_ids": user_id}}, upsert=True
            )
            await self.authdb.update_one(
                {"chat_id": chat_id}, {"$addToSet": {"user_ids": user_id}}
            )

    async def rm_auth(self, chat_id: int, user_id: int) -> None:
        users = await self._get_auth(chat_id)
        if user_id in users:
            users.discard(user_id)
            await self.authdb.update_one(
                {"_id": chat_id}, {"$pull": {"user_ids": user_id}}
            )
            await self.authdb.update_one(
                {"chat_id": chat_id}, {"$pull": {"user_ids": user_id}}
            )

    # ASSISTANT METHODS
    async def set_assistant(self, chat_id: int) -> int:
        num = randint(1, len(userbot.clients))
        await self.assistantdb.update_one(
            {"_id": chat_id},
            {"$set": {"num": num}},
            upsert=True,
        )
        self.assistant[chat_id] = num
        return num

    async def get_assistant(self, chat_id: int):
        from BADMUSIC import Bad

        if chat_id not in self.assistant:
            doc = await self.assistantdb.find_one({"_id": chat_id})
            if not doc:
                doc = await self.assistantdb.find_one({"chat_id": chat_id})
            num = doc["num"] if doc else await self.set_assistant(chat_id)
            self.assistant[chat_id] = num

        return Bad.clients[self.assistant[chat_id] - 1]

    async def get_client(self, chat_id: int):
        if chat_id not in self.assistant:
            await self.get_assistant(chat_id)
        return {1: userbot.one, 2: userbot.two, 3: userbot.three}.get(
            self.assistant[chat_id]
        )

    # BLACKLIST METHODS
    async def add_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            self.blacklisted.append(chat_id)
            return await self.cache.update_one(
                {"_id": "bl_chats"}, {"$addToSet": {"chat_ids": chat_id}}, upsert=True
            )
        await self.cache.update_one(
            {"_id": "bl_users"}, {"$addToSet": {"user_ids": chat_id}}, upsert=True
        )

    async def del_blacklist(self, chat_id: int) -> None:
        if str(chat_id).startswith("-"):
            self.blacklisted.remove(chat_id)
            return await self.cache.update_one(
                {"_id": "bl_chats"},
                {"$pull": {"chat_ids": chat_id}},
            )
        await self.cache.update_one(
            {"_id": "bl_users"},
            {"$pull": {"user_ids": chat_id}},
        )

    async def get_blacklisted(self, chat: bool = False) -> list[int]:
        if chat:
            if not self.blacklisted:
                doc = await self.cache.find_one({"_id": "bl_chats"})
                self.blacklisted.extend(doc.get("chat_ids", []) if doc else [])
            return self.blacklisted
        doc = await self.cache.find_one({"_id": "bl_users"})
        return doc.get("user_ids", []) if doc else []

    # CHAT METHODS
    async def is_chat(self, chat_id: int) -> bool:
        return chat_id in self.chats

    async def add_chat(self, chat_id: int) -> None:
        if not await self.is_chat(chat_id):
            self.chats.append(chat_id)
            await self.chatsdb.insert_one({"_id": chat_id})

    async def rm_chat(self, chat_id: int) -> None:
        if await self.is_chat(chat_id):
            result = await self.chatsdb.delete_one({"_id": chat_id})
            if result.deleted_count == 0:
                await self.chatsdb.delete_one({"chat_id": chat_id})
            self.chats.remove(chat_id)

    async def get_chats(self) -> list:
        if not self.chats:
            from bson import ObjectId
            loaded = set()
            async for chat in self.chatsdb.find():
                cid_key = chat.get("_id")
                if isinstance(cid_key, ObjectId):
                    cid = int(chat.get("chat_id", str(cid_key)))
                else:
                    cid = int(cid_key)
                if cid not in loaded:
                    self.chats.append(cid)
                    loaded.add(cid)
        return self.chats

    # LANGUAGE METHODS
    async def set_lang(self, chat_id: int, lang_code: str):
        await self.langdb.update_one(
            {"_id": chat_id},
            {"$set": {"lang": lang_code}},
            upsert=True,
        )
        self.lang[chat_id] = lang_code

    async def get_lang(self, chat_id: int) -> str:
        if chat_id not in self.lang:
            doc = await self.langdb.find_one({"_id": chat_id})
            if not doc:
                doc = await self.langdb.find_one({"chat_id": chat_id})
            self.lang[chat_id] = doc["lang"] if doc else "sm"
        return self.lang[chat_id]

    # LOGGER METHODS
    async def is_logger(self) -> bool:
        return self.logger

    async def get_logger(self) -> bool:
        doc = await self.cache.find_one({"_id": "logger"})
        if doc:
            self.logger = doc["status"]
        return self.logger

    async def set_logger(self, status: bool) -> None:
        self.logger = status
        await self.cache.update_one(
            {"_id": "logger"},
            {"$set": {"status": status}},
            upsert=True,
        )

    # PLAY MODE METHODS
    async def get_play_mode(self, chat_id: int) -> bool:
        if chat_id not in self.play_mode:
            doc = await self.playmodedb.find_one({"_id": chat_id})
            if not doc:
                doc = await self.playmodedb.find_one({"chat_id": chat_id})
            if doc:
                self.play_mode.append(chat_id)
        return chat_id in self.play_mode

    async def set_play_mode(self, chat_id: int, remove: bool = False) -> None:
        if remove:
            if chat_id in self.play_mode:
                result = await self.playmodedb.delete_one({"_id": chat_id})
                if result.deleted_count == 0:
                    await self.playmodedb.delete_one({"chat_id": chat_id})
                self.play_mode.remove(chat_id)
        else:
            self.play_mode.append(chat_id)
            await self.playmodedb.insert_one({"_id": chat_id})

    # SUDO METHODS
    async def add_sudo(self, user_id: int) -> None:
        await self.cache.update_one(
            {"_id": "sudoers"}, {"$addToSet": {"user_ids": user_id}}, upsert=True
        )

    async def del_sudo(self, user_id: int) -> None:
        await self.cache.update_one(
            {"_id": "sudoers"}, {"$pull": {"user_ids": user_id}}
        )

    async def get_sudoers(self) -> list[int]:
        doc = await self.cache.find_one({"_id": "sudoers"})
        return doc.get("user_ids", []) if doc else []

    # USER METHODS
    async def is_user(self, user_id: int) -> bool:
        return user_id in self.users

    async def add_user(self, user_id: int) -> None:
        if not await self.is_user(user_id):
            self.users.append(user_id)
            await self.usersdb.insert_one({"_id": user_id})

    async def rm_user(self, user_id: int) -> None:
        if await self.is_user(user_id):
            result = await self.usersdb.delete_one({"_id": user_id})
            if result.deleted_count == 0:
                await self.usersdb.delete_one({"user_id": user_id})
            try:
                await self.db.tgusersdb.delete_one({"user_id": user_id})
            except Exception:
                pass
            self.users.remove(user_id)

    async def get_users(self) -> list:
        if not self.users:
            from bson import ObjectId
            loaded = set()
            # Load from usersdb
            async for user in self.usersdb.find():
                uid_key = user.get("_id")
                if isinstance(uid_key, ObjectId):
                    uid = int(user.get("user_id", str(uid_key)))
                else:
                    uid = int(uid_key)
                if uid not in loaded:
                    self.users.append(uid)
                    loaded.add(uid)
            # Load from old tgusersdb if exists
            try:
                async for user in self.db.tgusersdb.find():
                    uid_key = user.get("_id")
                    if isinstance(uid_key, ObjectId):
                        uid = int(user.get("user_id", str(uid_key)))
                    else:
                        uid = int(uid_key)
                    if uid not in loaded:
                        self.users.append(uid)
                        loaded.add(uid)
            except Exception:
                pass  # No tgusersdb or error
        return self.users


    async def migrate_coll(self) -> None:
        logger.info("❖ ᴍɪɢʀᴀᴛɪɴɢ ᴜꜱᴇʀꜱ ᴀɴᴅ ᴄʜᴀᴛꜱ ꜰʀᴏᴍ ᴏʟᴅ ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ 🔥")

        from bson import ObjectId
        musers, mchats = [], []
        user_ids = set()
        chat_ids = set()

        # Migrate users
        ulist = [user async for user in self.db.tgusersdb.find()]
        ulist.extend([user async for user in self.usersdb.find()])

        for user in ulist:
            if "_id" not in user:
                continue
            if isinstance(user["_id"], ObjectId):
                user_id = int(user.get("user_id", str(user["_id"])))
            else:
                user_id = int(user["_id"])
            if user_id not in user_ids:
                user_ids.add(user_id)
                musers.append({"_id": user_id})

        await self.usersdb.drop()
        await self.db.tgusersdb.drop()
        if musers:
            await self.usersdb.insert_many(musers)

        # Migrate chats
        async for chat in self.chatsdb.find():
            if "_id" not in chat:
                continue
            if isinstance(chat["_id"], ObjectId):
                chat_id = int(chat.get("chat_id", str(chat["_id"])))
            else:
                chat_id = int(chat["_id"])
            if chat_id not in chat_ids:
                chat_ids.add(chat_id)
                mchats.append({"_id": chat_id})

        await self.chatsdb.drop()
        if mchats:
            await self.chatsdb.insert_many(mchats)

        await self.cache.insert_one({"_id": "migrated"})
        logger.info("❖ ᴍɪɢʀᴀᴛɪᴏɴ ᴄᴏᴍᴘʟᴇᴛᴇᴅ 🥀")

    async def load_cache(self) -> None:
        try:
            doc = await self.cache.find_one({"_id": "migrated"})
        except Exception as e:
            logger.error(f"Can't access cache for migration check: {e}")
            doc = None

        if not doc:
            try:
                await self.migrate_coll()
            except Exception as e:
                logger.error(f"❖ Migration failed: {type(e).__name__}: {e} 🥲")
            try:
                await self.cache.insert_one({"_id": "migrated"})
            except Exception as e:
                logger.warning(f"Can't mark migration as done: {e}")

        await self.get_chats()
        await self.get_users()
        await self.get_blacklisted(True)
        await self.get_logger()
        logger.info("❖ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄᴀᴄʜᴇ ʟᴏᴀᴅᴇᴅ ☠️")
