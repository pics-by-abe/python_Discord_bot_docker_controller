# Discord Docker controller

##### This is a simple discord bot that allows you to control your docker containers from discord

## Installation

### Requirements

- Docker
- Docker-compose

### Steps

1. Clone this repository
2. Create a discord bot and get the token in the [discord developer portal](https://discord.com/developers/applications)
3. Rename the **```.env.example```** file to **```.env```** and fill the change **```YOUR_TOKEN```** to your bot token
4. Run **```docker-compose up -d```** to start the bot
5. Invite the bot to your server
6. Run **```/help```** to see the available commands
7. Enjoy!

### Coming soon

- [ ] CPU, RAM and Network usage
- [ ] Create containers (with compose support)