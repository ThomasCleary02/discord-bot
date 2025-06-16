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
    description="Get a witty comeback from ChillBot's sarcastic side",
    guild=guild_obj
)
@app_commands.describe(
    topic="What should I give you a reality check about? (e.g., 'gaming skills', 'dating life', 'fashion sense')",
    user="Tag someone who needs humbled (optional)"
)
async def roast_command(interaction: discord.Interaction, topic: str = None, user: discord.User = None):
    """Roast command handler"""
    await interaction.response.defer()
    
    # Build clear instructions for the AI
    if user and topic:
        # Roast a specific user about a specific topic
        roast_target = f"<@{user.id}>"
        instructions = f"Roast {user.display_name} about their {topic}. Make it specific to {topic} and personal to them."
    elif user:
        # Just roast the user in general
        roast_target = f"<@{user.id}>"
        instructions = f"Give {user.display_name} a general roast. Make it about them personally but keep it playful."
    elif topic:
        # Roast a topic, directed at the command user
        roast_target = f"<@{interaction.user.id}>"
        instructions = f"Roast {interaction.user.display_name} about their {topic}. Focus on the {topic} specifically."
    else:
        # No parameters - roast the command user in general
        roast_target = f"<@{interaction.user.id}>"
        instructions = f"Give {interaction.user.display_name} a general roast. Be creative and snarky."
    
    try:
        # Pass clear instructions instead of mixed message/context
        roast_response = await get_ai_response(instructions, None, CLAUDE_TOKEN)
        response = f"{roast_target} {roast_response}"
            
        await interaction.followup.send(response)
        logger.info(f"Roast delivered by {interaction.user.display_name} - Topic: {topic}, User: {user}")
        
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

# --- Add a manual sync command for debugging ---
@bot.command(name="sync")
async def sync_commands(ctx):
    """Manual command to sync slash commands (for debugging)"""
    if ctx.author.id != 123456789:  # Replace with your Discord user ID
        await ctx.send("Only the bot owner can use this command.")
        return
    
    try:
        if guild_obj:
            synced = await bot.tree.sync(guild=guild_obj)
            await ctx.send(f"Synced {len(synced)} commands to this guild.")
        else:
            synced = await bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands globally.")
        
        for cmd in synced:
            logger.info(f"Synced: /{cmd.name}")
            
    except Exception as e:
        await ctx.send(f"Failed to sync: {e}")
        logger.error(f"Manual sync failed: {e}")

# --- Add clear commands for debugging ---
@bot.command(name="clear")
async def clear_commands(ctx):
    """Clear all slash commands (for debugging)"""
    if ctx.author.id != 123456789:  # Replace with your Discord user ID
        await ctx.send("Only the bot owner can use this command.")
        return
    
    try:
        if guild_obj:
            bot.tree.clear_commands(guild=guild_obj)
            await bot.tree.sync(guild=guild_obj)
            await ctx.send("Cleared guild commands.")
        else:
            bot.tree.clear_commands()
            await bot.tree.sync()
            await ctx.send("Cleared global commands.")
            
    except Exception as e:
        await ctx.send(f"Failed to clear: {e}")
        logger.error(f"Clear failed: {e}")
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

# --- Alternative roast command registration ---
async def setup_commands():
    """Setup slash commands after bot is ready"""
    
    @bot.tree.command(
        name="roast",
        description="Get a light-hearted roast from ChillBot",
        guild=guild_obj
    )
    @app_commands.describe(
        target="What or who should I roast?",
        user="Tag someone specific to roast (optional)"
    )
    async def roast_alt(interaction: discord.Interaction, topic: str = None, user: discord.User = None):
        await roast_command(interaction, topic, user)
    
    @bot.tree.command(
        name="ping", 
        description="Check if ChillBot is responsive",
        guild=guild_obj
    )
    async def ping_alt(interaction: discord.Interaction):
        await ping_command(interaction)
if __name__ == "__main__":
    logger.info("Starting ChillBot...")
    bot.run(TOKEN)