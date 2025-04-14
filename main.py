from utils.llm_client import get_ai_response
from dotenv import load_dotenv
import discord
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

TOKEN = os.getenv('DISCORD_TOKEN')
SERVER = os.getenv('DISCORD_GUILD')

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == SERVER:
            break

    print(
        f'{client.user} is connected to this server: \n'
        f'{guild.name} (id: {guild.id})'
    )

@client.event
async def on_message(message: discord.Message):
    user = str(message.author).split('#')[0]
    channel = str(message.channel.name)
    user_message = str(message.content)

    CLAUDE_TOKEN = os.getenv('ANTHROPIC_API_KEY')

    for mention in message.mentions:
        if mention == client.user:
            user_message = user_message.replace(f'<@{mention.id}>', "ChatBot")

    print(f'{user} said {user_message} in {channel}')

    if message.author == client.user:
        return
    
    if client.user in message.mentions:
        print("Message recieved")
        response = await get_ai_response(user_message, CLAUDE_TOKEN)
        await message.channel.send(f'{response}')

client.run(TOKEN)