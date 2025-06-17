import os
import logging
import discord
from discord.ext import commands
from utils.llm_client import get_ai_response

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ChillBot")

# --- Load .env in development only ---
if os.getenv("FLY_APP_NAME") is None:
    from dotenv import load_dotenv
    load_dotenv()

# --- Validate required environment variables ---
required_vars = ["DISCORD_TOKEN", "ANTHROPIC_API_KEY"]
for var in required_vars:
    if os.getenv(var) is None:
        raise EnvironmentError(f"Missing required environment variable: {var}")

# --- Load environment variables ---
TOKEN = os.getenv('DISCORD_TOKEN')
CLAUDE_TOKEN = os.getenv('ANTHROPIC_API_KEY')

# --- Discord Intents ---
intents = discord.Intents.default()
intents.message_content = True

# --- Bot Setup ---
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- On Bot Ready ---
@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")

# --- Welcome message on join ---
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                "Hey, I'm ChillBot! 👋 Just mention me to chat. "
                "Don't expect too much enthusiasm from me though."
            )
            break

# --- Message Handler ---
@bot.event
async def on_message(message: discord.Message):
    # Ignore own messages
    if message.author == bot.user:
        return
    
    # Check if bot is mentioned or if it's a DM
    if bot.user in message.mentions or isinstance(message.channel, discord.DMChannel):
        await handle_chat(message)

async def handle_chat(message: discord.Message):
    """Handle chat messages (mentions or DMs)"""
    user = message.author.display_name
    
    # Clean up the message content
    if isinstance(message.channel, discord.DMChannel):
        # In DMs, use the message as-is
        user_message = message.content.strip()
    else:
        # In servers, remove the bot mention
        user_message = message.content.replace(f'<@{bot.user.id}>', "ChillBot").strip()
    
    referenced_content = ""
    
    # Get referenced message if replying to the bot
    if message.reference:
        try:
            ref = await message.channel.fetch_message(message.reference.message_id)
            if ref.author == bot.user:
                referenced_content = ref.content
        except Exception as e:
            logger.warning(f"Failed to fetch referenced message: {e}")
    
    logger.info(f"Chat from {user}: {user_message}")
    if referenced_content:
        logger.info(f"Referenced bot message: {referenced_content}")
    
    # Show typing indicator
    async with message.channel.typing():
        try:
            response = await get_ai_response(user_message, referenced_content, CLAUDE_TOKEN)
            await message.channel.send(response)
        except Exception as e:
            logger.error(f"AI response error: {e}")
            await message.channel.send("Ugh, my brain isn't working right now. Try again later.")

@bot.event
async def on_command_error(ctx, error):
    """Handle any remaining command errors"""
    if isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors
        return
    
    logger.error(f"Command error: {error}")

if __name__ == "__main__":
    logger.info("Starting ChillBot...")
    bot.run(TOKEN)