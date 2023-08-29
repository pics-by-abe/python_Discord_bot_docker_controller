import discord
import os
from pathlib import Path
from datetime import datetime
from discord.ext import commands
import asyncio
import docker as dckr
from datetime import timezone


token = os.getenv("TOKEN")


async def run():
    description = "A cool discord bot."
    docker = dckr.from_env()
    launch = datetime.now(timezone.utc)
    bot = Bot(description=description, launch=launch, docker=docker)
    try:
        await bot.start(token)
    except KeyboardInterrupt:
        # Make sure to do these steps if you use a command to exit the bot
        await bot.logout()


class Bot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(
            description=kwargs.pop("description"),
            intents=discord.Intents.all()
        )
        self.docker = kwargs.pop("docker")
        self.launch = kwargs.pop("launch")
        for file in Path("cogs").glob("*.py"):
            name = file.stem
            if name.startswith('__'):
                continue
            self.load_extension(f"cogs.{name}")

    async def on_ready(self):
        print("Username: {0}\nID: {0.id}".format(self.user))

loop = asyncio.get_event_loop()

loop.run_until_complete(run())
