from discord.ext import commands
import discord
from utils import load_data
from config import config as cfg
from logger import logger as lgr


class AddSemesterRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = load_data()
        self.config = cfg
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣"]

    def _get_required_subjects(self, semester: int) -> list[str]:
        df = self.data[semester - 1]
        pov = df[df["Pov"] == "P"]

        names = pov["Zkr"].unique().tolist()

        return names

    async def _init_semesters(self) -> None:
        lgr.info("Initializing semester permissions")
        server_id = self.config['server_id']
        role_colors = ["eb9334", "a3551d",
                       "5feb34", "1da33c", "34cfeb", "1d77a3"]

        guild = self.bot.get_guild(server_id)

        for idx, data in enumerate(self.data, 1):
            role_name = f"{(idx/2):.1f}bit"

            role = discord.utils.get(guild.roles, name=role_name)

            permissions = discord.Permissions(998616981057)
            if not role:

                role = await guild.create_role(name=role_name, color=discord.Color(int(role_colors[idx - 1], 16)), hoist=True, mentionable=True, permissions=permissions)
                lgr.info(f"Created role {role_name}")
            else:
                await role.edit(permissions=permissions)

            category_name = f"{idx}.semester"

            category = discord.utils.get(guild.categories, name=category_name)
            if not category:
                overwrites = {
                    guild.default_role: discord.PermissionOverwrite(view_channel=False, read_messages=False),
                    role: discord.PermissionOverwrite(view_channel=True, read_messages=True),
                }
                category = await guild.create_category(category_name, position=0, overwrites=overwrites)
                lgr.info(f"Created category {category_name}")

            data = self._get_required_subjects(idx)

            for name in data + [f"general-{idx}"]:
                channel_name = f"{name.lower()}"

                channel = discord.utils.get(guild.channels, name=channel_name)
                if not channel:
                    channel = await guild.create_text_channel(channel_name, category=category, position=0)
                    lgr.info(f"Created channel {channel_name}")

    async def _init_semester_message(self) -> None:
        lgr.info("Initializing semester message")
        channel = self.bot.get_channel(self.config['bot_channel'])

        if channel is None:
            return

        history = [msg async for msg in channel.history(limit=1)]
        if len(history) > 0:
            return
        message = "React to this message to get your semester role pyco!\n\n"

        message = await channel.send(message)

        for emoji in self.emojis:
            await message.add_reaction(emoji)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload) -> None:
        user, reaction, channel_id, message_id = payload.member, payload.emoji, payload.channel_id, payload.message_id

        lgr.info(f"Reaction added by {user.name}")

        if user.bot:
            return

        if channel_id != self.config['bot_channel'] or message_id != self.config['semester_message']:
            return

        if str(reaction) not in self.emojis:
            return

        guild = self.bot.get_guild(self.config['server_id'])
        role = discord.utils.get(
            guild.roles, name=f"{((self.emojis.index(str(reaction)) + 1)/2):.1f}bit")
        await user.add_roles(role)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload) -> None:
        user_id, reaction, channel_id, message_id = payload.user_id, payload.emoji, payload.channel_id, payload.message_id

        user = discord.utils.get(
            self.bot.get_all_members(), id=user_id)
        lgr.info(f"Reaction removed")

        if channel_id != self.config['bot_channel'] or message_id != self.config['semester_message']:
            return

        if str(reaction) not in self.emojis:
            return

        guild = self.bot.get_guild(self.config['server_id'])
        role = discord.utils.get(
            guild.roles, name=f"{((self.emojis.index(str(reaction)) + 1)/2):.1f}bit")

        await user.remove_roles(role)

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self._init_semester_message()
        await self._init_semesters()


def setup(bot):
    bot.add_cog(AddSemesterRoles(bot))
