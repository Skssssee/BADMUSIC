from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.API_ID = int(getenv("API_ID", 0))
        self.API_HASH = getenv("API_HASH")

        self.BOT_TOKEN = getenv("BOT_TOKEN")
        self.MONGO_URL = getenv("MONGO_URL")

        self.LOGGER_ID = int(getenv("LOGGER_ID", 0))
        self.OWNER_ID = int(getenv("OWNER_ID", 0))

        self.SESSION1 = getenv("SESSION", None)
        self.SESSION2 = getenv("SESSION2", None)
        self.SESSION3 = getenv("SESSION3", None)

        self.API_URL = getenv("API_URL", "http://47.129.201.23:2020/try")
        self.API_ENABLED = bool(getenv("API_ENABLED", "True"))
        self.COOKIES_ENABLED = bool(getenv("COOKIES_ENABLED", "False"))

        self.SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/PBX_UPDATE")
        self.SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/PBX_CHAT")

        self.AUTO_LEAVE: bool = getenv("AUTO_LEAVE", False)
        self.DEFAULT_THUMB = getenv("DEFAULT_THUMB", "")
        self.PING_IMG = getenv("PING_IMG", "https://files.catbox.moe/haagg2.png")
        
        self.START_IMG = [
            "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
            "https://graph.org/file/69ba894371860cd22d92e.jpg",
            "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
            "https://graph.org/file/3a400f1f32fc381913061.jpg",
            "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
            "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
            "https://graph.org/file/25e215c4602b241b66829.jpg",
            "https://graph.org/file/a13e9733afdad69720d67.jpg",
            "https://graph.org/file/692e89f8fe20554e7a139.jpg",
            "https://graph.org/file/db277a7810a3f65d92f22.jpg",
            "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
            "https://graph.org/file/f86b71018196c5cfe7344.jpg",
            "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
            "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
            "https://graph.org/file/84de4b440300297a8ecb3.jpg",
            "https://graph.org/file/84e84ff778b045879d24f.jpg",
            "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
            "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
            "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
            "https://graph.org/file/37248e7bdff70c662a702.jpg",
            "https://graph.org/file/0bfe29d15e918917d1305.jpg",
            "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
            "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
            "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
            "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
            "https://graph.org/file/39d7277189360d2c85b62.jpg",
            "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
            "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
            "https://graph.org/file/3514efaabe774e4f181f2.jpg",  
            "https://graph.org/file/eaa3a2602e43844a488a5.jpg",
            "https://graph.org/file/b129e98b6e5c4db81c15f.jpg",
            "https://graph.org/file/3ccb86d7d62e8ee0a2e8b.jpg",
            "https://graph.org/file/df11d8257613418142063.jpg",
            "https://graph.org/file/9e23720fedc47259b6195.jpg",
            "https://graph.org/file/826485f2d7db6f09db8ed.jpg",
            "https://graph.org/file/ff3ad786da825b5205691.jpg",
            "https://graph.org/file/52713c9fe9253ae668f13.jpg",
            "https://graph.org/file/8f8516c86677a8c91bfb1.jpg",
            "https://graph.org/file/6603c3740378d3f7187da.jpg",
            "https://graph.org/file/66cb6ec40eea5c4670118.jpg",
            "https://graph.org/file/2e3cf4327b169b981055e.jpg",   
        ]

        self.HELP_IMG = [
            "https://graph.org/file/f76fd86d1936d45a63c64.jpg",
            "https://graph.org/file/69ba894371860cd22d92e.jpg",
            "https://graph.org/file/67fde88d8c3aa8327d363.jpg",
            "https://graph.org/file/3a400f1f32fc381913061.jpg",
            "https://graph.org/file/a0893f3a1e6777f6de821.jpg",
            "https://graph.org/file/5a285fc0124657c7b7a0b.jpg",
            "https://graph.org/file/25e215c4602b241b66829.jpg",
            "https://graph.org/file/a13e9733afdad69720d67.jpg",
            "https://graph.org/file/692e89f8fe20554e7a139.jpg",
            "https://graph.org/file/db277a7810a3f65d92f22.jpg",
            "https://graph.org/file/a00f89c5aa75735896e0f.jpg",
            "https://graph.org/file/f86b71018196c5cfe7344.jpg",
            "https://graph.org/file/a3db9af88f25bb1b99325.jpg",
            "https://graph.org/file/5b344a55f3d5199b63fa5.jpg",
            "https://graph.org/file/84de4b440300297a8ecb3.jpg",
            "https://graph.org/file/84e84ff778b045879d24f.jpg",
            "https://graph.org/file/a4a8f0e5c0e6b18249ffc.jpg",
            "https://graph.org/file/ed92cada78099c9c3a4f7.jpg",
            "https://graph.org/file/d6360613d0fa7a9d2f90b.jpg",
            "https://graph.org/file/37248e7bdff70c662a702.jpg",
            "https://graph.org/file/0bfe29d15e918917d1305.jpg",
            "https://graph.org/file/16b1a2828cc507f8048bd.jpg",
            "https://graph.org/file/e6b01f23f2871e128dad8.jpg",
            "https://graph.org/file/cacbdddee77784d9ed2b7.jpg",
            "https://graph.org/file/ddc5d6ec1c33276507b19.jpg",
            "https://graph.org/file/39d7277189360d2c85b62.jpg",
            "https://graph.org/file/5846b9214eaf12c3ed100.jpg",
            "https://graph.org/file/ad4f9beb4d526e6615e18.jpg",
            "https://graph.org/file/3514efaabe774e4f181f2.jpg",  
            "https://graph.org/file/eaa3a2602e43844a488a5.jpg",
            "https://graph.org/file/b129e98b6e5c4db81c15f.jpg",
            "https://graph.org/file/3ccb86d7d62e8ee0a2e8b.jpg",
            "https://graph.org/file/df11d8257613418142063.jpg",
            "https://graph.org/file/9e23720fedc47259b6195.jpg",
            "https://graph.org/file/826485f2d7db6f09db8ed.jpg",
            "https://graph.org/file/ff3ad786da825b5205691.jpg",
            "https://graph.org/file/52713c9fe9253ae668f13.jpg",
            "https://graph.org/file/8f8516c86677a8c91bfb1.jpg",
            "https://graph.org/file/6603c3740378d3f7187da.jpg",
            "https://graph.org/file/66cb6ec40eea5c4670118.jpg",
            "https://graph.org/file/2e3cf4327b169b981055e.jpg",   
        ]
        
        self.VIDEO_PLAY: bool = getenv("VIDEO_PLAY", True)

    def check(self):
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID", "SESSION1"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"ᴍɪꜱꜱɪɴɢ ʀᴇQᴜɪʀᴇᴅ ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ ᴠᴀʀɪᴀʙʟᴇꜱ: {', '.join(missing)}")
