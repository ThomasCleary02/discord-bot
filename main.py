import os
import logging
import discord
from discord import app_commands
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
required_vars = ["DISCORD_TOKEN", "DISCORD_GUILD_ID", "ANTHROPIC_API_KEY"]
for var in required_vars:
    if os.getenv(var) is None:
        raise EnvironmentError(f"Missing required environment variable: {var}")

# --- Load environment variables ---
TOKEN = os.getenv('DISCORD_TOKEN')
CLAUDE_TOKEN = os.getenv('ANTHROPIC_API_KEY')
GUILD_ID = int(os.getenv('DISCORD_GUILD_ID'))
guild_obj = discord.Object(id=GUILD_ID)

# --- Discord Intents ---
intents = discord.Intents.default()
intents.message_content = True

# --- Bot Setup ---
bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), intents=intents)
tree = bot.tree

# --- On Bot Ready ---
@bot.event
async def on_ready():
    try:
        await tree.sync(guild=guild_obj)  # Sync to dev server only
        logger.info(f"{bot.user} is ready and synced to guild {GUILD_ID}!")
    except Exception as e:
        logger.error(f"Error syncing commands: {e}")

# --- Welcome message on join (optional) ---
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                "Hey, I'm ChillBot. Mention me or try `/roast` to get started. Just don't expect enthusiasm."
            )
            break

# --- Message Listener for Mentions ---
@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)  # Let commands run

    if bot.user in message.mentions:
        user = message.author.display_name
        user_message = message.content.replace(f'<@{bot.user.id}>', "ChillBot")
        referenced_content = ""

        if message.reference:
            try:
                ref = await message.channel.fetch_message(message.reference.message_id)
                if ref.author == bot.user:
                    referenced_content = ref.content
            except Exception as e:
                logger.warning(f"Failed to fetch referenced message: {e}")

        logger.info(f"Message from {user}: {user_message}")
        if referenced_content:
            logger.info(f" -- in reply to ChillBot: {referenced_content}")

        try:
            response = await get_ai_response(user_message, referenced_content, CLAUDE_TOKEN)
            await message.channel.send(response)
        except Exception as e:
            logger.error(f"AI response error: {e}")
            await message.channel.send("Wow, I'm drawing a blank. Try again later.")

# --- Slash Command: /roast ---
@tree.command(
    name="roast",
    description="Request a light-hearted roast from ChillBot",
    guild=guild_obj  # Change to global for production-wide rollout
)
@app_commands.describe(
    message="What should ChillBot roast?",
    user="Optionally tag someone to roast them."
)
async def roast(interaction: discord.Interaction, message: str, user: discord.User = None):
    await interaction.response.defer()

    target = f"<@{user.id}>" if user else "you"
    context = f"This roast is about {target}."
    full_message = f"Roast request: {message}"

    try:
        roast_response = await get_ai_response(full_message, context, CLAUDE_TOKEN)
        await interaction.followup.send(f"{target}, {roast_response}")
    except Exception as e:
        logger.error(f"Roast command error: {e}")
        await interaction.followup.send("Oops. ChillBot couldn't come up with anything clever right now.")

# --- Start the Bot ---
bot.run(TOKEN)
