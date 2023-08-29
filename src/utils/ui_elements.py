import discord
import docker

class Buttons(discord.ui.View):
    @discord.ui.button(label="Start", style=discord.ButtonStyle.green, emoji="▶️")
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Started", ephemeral=True)
        container = interaction.message.embeds[0].title.split(" ")[1]
        dckr = docker.from_env()
        container = dckr.containers.get(container)
        container.start()
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.red, emoji="⏹️")
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Stopped", ephemeral=True)
        container = interaction.message.embeds[0].title.split(" ")[1]
        dckr = docker.from_env()
        container = dckr.containers.get(container)
        container.stop()
    @discord.ui.button(label="Restart", style=discord.ButtonStyle.blurple, emoji="🔄")
    async def restart(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Restarted", ephemeral=True)
        #* get container name
        container = interaction.message.embeds[0].title.split(" ")[1]
        dckr = docker.from_env()
        container = dckr.containers.get(container)
        container.restart()
    @discord.ui.button(label="Stop & Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def delete(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.send_message("Deleted", ephemeral=True)
        container = interaction.message.embeds[0].title.split(" ")[1]
        dckr = docker.from_env()
        container = dckr.containers.get(container)
        container.stop()
        container.remove()

