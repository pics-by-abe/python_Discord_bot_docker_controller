import discord
from discord.ext import commands, tasks
from discord.ext.pages import PaginatorButton, Paginator
from datetime import datetime
from utils.ui_elements import Buttons

containers_list = []

class Docker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.docker = bot.docker
        #* start docker loop
        self.docker_loop.start()
    #* stop docker loop
    def cog_unload(self):
        self.docker_loop.cancel()
    #* loop running docker container
    @tasks.loop(seconds=5)
    async def docker_loop(self):
        for container in self.docker.containers.list(all=True):
            #* if container is not in list, append it
            if container.name not in containers_list:
                containers_list.append(container.name)

    #* container command to manage docker containers, /container (name) , autocomplete , slash command
    @commands.slash_command(name="container", description="Manage docker containers")
    async def container(self, ctx, name: discord.Option(discord.SlashCommandOptionType.string, description="Name of the radio station to remove", required=True, autocomplete=discord.utils.basic_autocomplete(containers_list))):
        #* get container by name
        container = self.docker.containers.get(name)
        embed = discord.Embed(
            title=f"Container {container.name}", color=discord.Color.random())
        #* image name
        embed.add_field(name="Image", value=container.image.tags[0], inline=False)
        #* container id
        embed.add_field(name="ID", value=container.id, inline=False)
        #* container status
        embed.add_field(name="Status", value=container.status, inline=False)
        #* container running for how long (year, month, day, hour, minute, second)
        started_at_str = str(container.attrs['State']['StartedAt'])
        current_time_str = str(datetime.now())
        #* Truncate the fractional seconds to 6 decimal places
        started_at_str = f'{started_at_str[:26]}Z'
        #* Convert strings to datetime objects
        started_at = datetime.strptime(started_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        current_time = datetime.strptime(current_time_str, "%Y-%m-%d %H:%M:%S.%f")
        #* Calculate the time difference
        time_difference = current_time - started_at
        embed.add_field(name="Running for", value=str(time_difference).split(".")[0], inline=False)
        formated_ports = ""
        for port, values in container.ports.items():
            if values is not None and len(values) > 0:
                host_port = values[0]['HostPort']
                formated_ports += f"{host_port}:{port}\n"
        embed.add_field(name="Ports", value=formated_ports.strip() or "None", inline=False)
        formated_ips = "".join(
            f"{network}: {values['IPAddress']}\n"
            for network, values in container.attrs['NetworkSettings'][
                'Networks'
            ].items()
        )
        embed.add_field(name="Networks + IP(v4)", value=formated_ips.strip() or "None", inline=False)
        #* created at
        created_at_str = str(container.attrs['State']['StartedAt'])
        created_at_str = f'{created_at_str[:26]}Z'
        created_at = datetime.strptime(created_at_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        embed.add_field(name="Created at", value=str(created_at).split(".")[0], inline=False)
        #* restart policy
        embed.add_field(name="Restart policy", value=container.attrs['HostConfig']['RestartPolicy']['Name'], inline=False)
        #* add footer
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar)
        
        view = Buttons()
        await ctx.respond(embed=embed, view=view)

    #* container command error handler
    @container.error
    async def container_error(self, ctx, error):
        await ctx.respond(f"Error:\n```{error}```", ephemeral=True)
    
    #* containers command to list all docker containers, /containers , slash command
    @commands.slash_command(name="containers", description="List all docker containers")
    async def containers(self, ctx):
        pages = []
        buttons = [
            PaginatorButton("first", label="⏪", style=discord.ButtonStyle.red),
            PaginatorButton("prev", label="◀️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("page_indicator", disabled=True),
            PaginatorButton("next", label="▶️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("last", label="⏩", style=discord.ButtonStyle.red)
        ]
        containers = [container.name for container in self.docker.containers.list(all=True)]
        containers.sort()
        #* embed with max. 15 containers per page, all sorted alphabetically
        for i in range(0, len(containers), 15):
            embed = discord.Embed(
                title="Docker containers", color=discord.Color.random())
            #* status of each container (running, stopped, exited) as emoji, behind container name
            for container in containers[i:i+15]:
                container = self.docker.containers.get(container)
                if container.status == "running":
                    embed.add_field(name=f"{container.name} | :green_circle:", value="", inline=False)
                elif container.status == "exited":
                    embed.add_field(name=f"{container.name} | :red_circle:", value="", inline=False)
                elif container.status == "paused":
                    embed.add_field(name=f"{container.name} | :yellow_circle:", value="", inline=False)
                else:
                    embed.add_field(name=f"{container.name} | :white_circle:", value="", inline=False)
            #
            
            # embed.description = "\n".join(containers[i:i+15])
            #* add displaying x-y of z containers
            start_idx = i + 1
            end_idx = min(start_idx + 14, len(containers))
            embed.set_footer(text=f"Displaying {start_idx}-{end_idx} of {len(containers)} containers")
            pages.append(embed)
        paginator = Paginator(
            pages=pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons
        )
        #* send paginator
        await paginator.respond(ctx.interaction)
    
    #* containers command error handler
    @containers.error
    async def containers_error(self, ctx, error):
        await ctx.respond(f"Error:\n```{error}```", ephemeral=True)

    #* images command to list all docker images, /images , slash command, Used yes/no
    @commands.slash_command(name="images", description="List all docker images")
    async def images(self, ctx):
        pages = []
        buttons = [
            PaginatorButton("first", label="⏪", style=discord.ButtonStyle.red),
            PaginatorButton("prev", label="◀️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("page_indicator", disabled=True),
            PaginatorButton("next", label="▶️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("last", label="⏩", style=discord.ButtonStyle.red)
        ]
        images = [image.tags[0] for image in self.docker.images.list(all=True) if image.tags]
        images.sort()
        #* Split the images list into chunks of 15 images each
        image_chunks = [images[i:i+15] for i in range(0, len(images), 15)]
        #* Create a list to store the embed pages
        pages = []
        #* Iterate through each chunk of images
        for i, chunk in enumerate(image_chunks):
            embed = discord.Embed(
                title="Docker images", color=discord.Color.random())
            embed.description = "\n".join(chunk)
            #* Calculate the range of displayed images
            start_idx = i * 15 + 1
            end_idx = min(start_idx + 14, len(images))
            embed.set_footer(text=f"Displaying {start_idx}-{end_idx} of {len(images)} images")
            pages.append(embed)
        paginator = Paginator(
            pages=pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons
        )
        #* send paginator
        await paginator.respond(ctx.interaction)
    #* images command error handler
    @images.error
    async def images_error(self, ctx, error):
        await ctx.respond(f"Error:\n```{error}```", ephemeral=True)

    #* logs command to get log from docker container, /log (name) , autocomplete , slash command, last 100 lines
    @commands.slash_command(name="log", description="Get log from docker container")
    async def log(self, ctx, name: discord.Option(discord.SlashCommandOptionType.string, description="Name of the container you want to check the log", required=True, autocomplete=discord.utils.basic_autocomplete(containers_list))):
        #* multiple pages if log is longer than 2000 characters
        pages = []
        buttons = [
            PaginatorButton("first", label="⏪", style=discord.ButtonStyle.red),
            PaginatorButton("prev", label="◀️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("page_indicator", disabled=True),
            PaginatorButton("next", label="▶️",
                            style=discord.ButtonStyle.green),
            PaginatorButton("last", label="⏩", style=discord.ButtonStyle.red)
        ]
        #* get container by name
        container = self.docker.containers.get(name)
        #* get log
        log = container.logs(tail=100).decode("utf-8")
        #* split log into chunks of 2000 characters
        log_chunks = [log[i:i+2000] for i in range(0, len(log), 2000)]
        #* create embed for each chunk
        for chunk in log_chunks:
            embed = discord.Embed(
                title=f"Log from {container.name}", description=f"```{chunk}```", color=discord.Color.random())
            pages.append(embed)
        paginator = Paginator(
            pages=pages,
            show_indicator=True,
            use_default_buttons=False,
            custom_buttons=buttons
        )
        #* send paginator
        await paginator.respond(ctx.interaction)

    #* log command error handler
    @log.error
    async def log_error(self, ctx, error):
        await ctx.respond(f"Error:\n```{error}```", ephemeral=True)



    #* exec command to execute command in docker container, /exec (name) (command) , autocomplete (name), slash command
    @commands.slash_command(name="exec", description="Execute command in docker container")
    async def exec(self, ctx, name: discord.Option(discord.SlashCommandOptionType.string, description="Name of the container you want to execute the command in", required=True, autocomplete=discord.utils.basic_autocomplete(containers_list)), command: discord.Option(discord.SlashCommandOptionType.string, description="Command you want to execute", required=True)):
        #* get container by name
        container = self.docker.containers.get(name)
        #* execute command
        exec = container.exec_run(command)
        #* send output
        await ctx.respond(f"```{exec.output.decode('utf-8')}```", ephemeral=True)

    #* exec command error handler
    @exec.error
    async def exec_error(self, ctx, error):
        await ctx.respond(f"Error:\n```{error}```", ephemeral=True)


    #** help command
    @commands.slash_command(name="help", description="Show help")
    async def help(self, ctx):
        #* get all cogs and commands, only one page
        for cog in self.bot.cogs:
            cog = self.bot.get_cog(cog)
            embed = discord.Embed(
                title=f"{cog.qualified_name} Commands", description=f"Commands for {cog.qualified_name}", color=discord.Color.random())
            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar)
            embed.set_thumbnail(url=self.bot.user.avatar)
            for command in cog.get_commands():
                embed.add_field(name=f"{command.name}",
                                value=command.description, inline=False)
        await ctx.respond(embed=embed)

    
def setup(self):
    self.add_cog(Docker(self))
