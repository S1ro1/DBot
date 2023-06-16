import discord
from discord.ext import commands
from config import config as cfg


intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.reactions = True
intents.members = True


class DBot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = cfg

    async def on_ready(self):
        print("Logged in and ready to serve!")


TOKEN = cfg.get("bot_token")
bot = DBot(command_prefix=">", intents=intents)
bot.load_extension("cogs.semester_roles")
bot.run(TOKEN)
