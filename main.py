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
required_vars = ["DISCORD_TOKEN", "ANTHROPIC_API_KEY"]
for var in required_vars:
    if os.getenv(var) is None:
        raise EnvironmentError(f"Missing required environment variable: {var}")

# --- Load environment variables ---
TOKEN = os.getenv('DISCORD_TOKEN')
CLAUDE_TOKEN = os.getenv('ANTHROPIC_API_KEY')

# Optional: Only use GUILD_ID for development/testing
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
if GUILD_ID:
    GUILD_ID = int(GUILD_ID)
    guild_obj = discord.Object(id=GUILD_ID)
else:
    guild_obj = None

# --- Discord Intents ---
intents = discord.Intents.default()
intents.message_content = True

# --- Bot Setup ---
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- On Bot Ready ---
@bot.event
async def on_ready():
    logger.info(f"{bot.user} has connected to Discord!")
    
    try:
        if guild_obj:
            # Development: Sync to specific guild (instant)
            synced = await bot.tree.sync(guild=guild_obj)
            logger.info(f"Synced {len(synced)} commands to development guild {GUILD_ID}")
        else:
            # Production: Sync globally (takes up to 1 hour)
            synced = await bot.tree.sync()
            logger.info(f"Synced {len(synced)} commands globally")
            
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# --- Welcome message on join ---
@bot.event
async def on_guild_join(guild):
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            await channel.send(
                "Hey, I'm ChillBot! 👋 Mention me to chat or use `/roast` for some light roasting. "
                "Just don't expect too much enthusiasm from me."
            )
            break

# --- Message Handler ---
@bot.event
async def on_message(message: discord.Message):
    # Ignore own messages
    if message.author == bot.user:
        return
    
    # Process commands first (messages starting with !)
    if message.content.startswith(bot.command_prefix):
        await bot.process_commands(message)
        return
    
    # Handle mentions
    if bot.user in message.mentions:
        await handle_mention(message)

async def handle_mention(message: discord.Message):
    """Handle when the bot is mentioned in a message"""
    user = message.author.display_name
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
    
    logger.info(f"Mention from {user}: {user_message}")
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

# --- Slash Command: /roast ---
@bot.tree.command(
    name="roast",
    description="Get a light-hearted roast from ChillBot",
    guild=guild_obj  # None for global, guild_obj for development
)
@app_commands.describe(
    target="What or who should I roast?",
    user="Tag someone specific to roast (optional)"
)
async def roast_command(interaction: discord.Interaction, target: str, user: discord.User = None):
    """Roast command handler"""
    await interaction.response.defer()
    
    # Determine the target
    if user:
        roast_target = f"<@{user.id}>"
        context = f"Roast this person: {user.display_name}. "
    else:
        roast_target = "you"
        context = ""
    
    context += f"The roast request is about: {target}"
    full_message = f"Give me a clever, light-hearted roast about: {target}"
    
    try:
        roast_response = await get_ai_response(full_message, context, CLAUDE_TOKEN)
        
        # Format the response
        if user:
            response = f"{roast_target} {roast_response}"
        else:
            response = roast_response
            
        await interaction.followup.send(response)
        logger.info(f"Roast delivered by {interaction.user.display_name}: {target}")
        
    except Exception as e:
        logger.error(f"Roast command failed: {e}")
        await interaction.followup.send(
            "Even I can't come up with a good roast right now. That's embarrassing."
        )

# --- Simple ping command for testing ---
@bot.tree.command(
    name="ping", 
    description="Check if ChillBot is responsive",
    guild=guild_obj
)
async def ping_command(interaction: discord.Interaction):
    """Simple ping command"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"Pong! 🏓 Latency: {latency}ms")

# --- Error handlers ---
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command errors"""
    logger.error(f"Slash command error: {error}")
    
    if not interaction.response.is_done():
        await interaction.response.send_message(
            "Something went wrong with that command. Try again?", 
            ephemeral=True
        )
    else:
        await interaction.followup.send(
            "Something went wrong with that command. Try again?", 
            ephemeral=True
        )

@bot.event
async def on_command_error(ctx, error):
    """Handle prefix command errors"""
    if isinstance(error, commands.CommandNotFound):
        # Ignore command not found errors for prefix commands
        return
    
    logger.error(f"Command error: {error}")
    await ctx.send("Something went wrong. Maybe try a slash command instead?")

# --- Start the Bot ---
if __name__ == "__main__":
    logger.info("Starting ChillBot...")
    bot.run(TOKEN)