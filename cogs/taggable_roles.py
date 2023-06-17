from discord.ext import commands
import discord
from utils import load_data
from config import config as cfg
from logger import logger as lgr
from pymongo import MongoClient


class TaggableRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.created_roles = {}
        self.db = self._setup_db()

    def _setup_db(self):
        client = MongoClient(cfg.get("db_url"))
        db = client["test"]
        collection = db["taggable_roles"]
        return collection

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        lgr.info("TaggableRoles cog loaded")

    @discord.slash_command(name="create_taggable_role", description="Create a taggable role")
    @commands.check(lambda ctx: ctx.channel.id == cfg.get("command_channel"))
    async def create_taggable(self, ctx, role: discord.Option(str, description="The role to create", required=True)):
        await ctx.guild.create_role(name=role, mentionable=True)
        lgr.info(f"Created role {role}")
        await ctx.respond(f"Created role {role}. React on this message with 👍 to get the role!")

        async for msg in ctx.channel.history():
            if msg.author == ctx.guild.me:
                await msg.add_reaction("👍")
                self.db.insert_one({"message_id": msg.id, "role": role})
                break

    @discord.slash_command(name="delete_taggable_role", description="Delete a taggable role")
    @commands.check(lambda ctx: ctx.channel.id == cfg.get("command_channel"))
    async def delete_taggable(self, ctx, role: discord.Option(discord.Role, description="The role to delete", required=True)):
        query = {"role": role.name}

        result = self.db.find_one(query)
        if not result:
            await ctx.respond(f"Role {role.name} could not be deleted!")
            return

        await role.delete()
        self.db.delete_one(query)
        lgr.info(f"Deleted role {role.name}")

        await ctx.respond(f"Deleted role {role}")

        msg = await ctx.channel.fetch_message(result["message_id"])
        await msg.delete()

    @commands.Cog.listener()
    @commands.check(lambda payload: payload.channel_id == cfg.get("command_channel"))
    async def on_raw_reaction_add(self, payload) -> None:
        user, reaction, message_id = payload.member, payload.emoji, payload.message_id

        if str(reaction) != "👍":
            return

        result = self.db.find_one({"message_id": message_id})

        if not result:
            return

        if user.bot:
            return

        guild = self.bot.get_guild(cfg.get("server_id"))
        role = discord.utils.get(guild.roles, name=result["role"])

        lgr.info(f"Adding role {role.name} to {user.name}")
        await user.add_roles(role)

    @commands.Cog.listener()
    @commands.check(lambda payload: payload.channel_id == cfg.get("command_channel"))
    async def on_raw_reaction_remove(self, payload) -> None:
        user_id, reaction, message_id = payload.user_id, payload.emoji, payload.message_id

        if str(reaction) != "👍":
            return

        result = self.db.find_one({"message_id": message_id})

        if not result:
            return

        user = discord.utils.get(self.bot.get_all_members(), id=user_id)

        guild = self.bot.get_guild(cfg.get("server_id"))
        role = discord.utils.get(guild.roles, name=result["role"])

        lgr.info(f"Removing role {role.name} from {user.name}")
        await user.remove_roles(role)


def setup(bot):
    bot.add_cog(TaggableRoles(bot))
