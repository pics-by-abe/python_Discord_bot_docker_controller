import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_loop.start()

    def cog_unload(self):
        self.status_loop.cancel()

    #*status loop
    @tasks.loop(seconds=120)
    async def status_loop(self):
        container_count = len(self.bot.docker.containers.list())
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{container_count} containers"))
        await asyncio.sleep(120)
        uptime = datetime.now(timezone.utc) - self.bot.launch
        await self.bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"{uptime}"))

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Events(bot))