import discord
from discord.ext import commands
from config import config as cfg

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.reactions = True
intents.members = True

bot = commands.Bot(command_prefix='>', intents=intents)


class DBot(commands.Bot):
    async def setup_hook(self):
        self.config = cfg
        await self.load_extension("cogs.semester_roles")

    async def on_ready(self):
        print("Logged in and ready to serve!")


TOKEN = cfg.get("bot_token")
bot = DBot(command_prefix=">", intents=intents)
bot.run(TOKEN)
