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

    # Get referenced message and author if reply
    referenced_message = None
    referenced_content = ""
    if message.reference:
        referenced_message = await message.channel.fetch_message(message.reference.message_id)
        referenced_author = referenced_message.author
        referenced_content = referenced_message.content
        if referenced_author == client.user:
            referenced_content = referenced_message.content

    CLAUDE_TOKEN = os.getenv('ANTHROPIC_API_KEY')

    for mention in message.mentions:
        if mention == client.user:
            user_message = user_message.replace(f'<@{mention.id}>', "ChillBot")

    print(f'{user} said {user_message} in {channel}')
    if referenced_message:
        print(f" -- this is a reply to {referenced_author} who said: {referenced_content}")

    if message.author == client.user:
        return
    
    if client.user in message.mentions:
        print("Message recieved")
        response = await get_ai_response(user_message, referenced_content, CLAUDE_TOKEN)
        await message.channel.send(f'{response}')

client.run(TOKEN)