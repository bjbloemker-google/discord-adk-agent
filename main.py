import os
import asyncio
import random
import uuid
import discord
from discord.ext import commands
from dotenv import load_dotenv
# ADK
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

# Initialization asd sadf d

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

created_channels = {}
channel_lock = asyncio.Lock()

ADJECTIVES = [
    "Helpful", "Kind", "Clever", "Brave", "Wise",
    "Happy", "Gentle", "Calm", "Eager", "Proud"
]
NAMES = [
    "Alex", "Jordan", "Taylor", "Casey", "Riley",
    "Jamie", "Morgan", "Skyler", "Quinn", "Peyton"
]

## Basic ADK Agent
adk_agent = Agent(
    model='gemini-2.0-flash',
    name='discord_agent',
    description='A helpful assistant for user questions in Discord channels.',
    instruction='Your name is {channel_name}. You are talking with a person named {user}. Answer user questions to the best of your knowledge and engage in helpful conversation.',
    tools=[google_search]
)
session_service_stateful = InMemorySessionService()

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return
    
    if message.content.lower().startswith('!exit'):
        await message.channel.send('Bye bye!')
        # will be proccessed by !exit command
        await bot.process_commands(message)
        return

    guild_id = message.guild.id
    channel_id = message.channel.id

    # Porcess the message if it is in an AI channel
    if guild_id in created_channels and channel_id in created_channels[guild_id] and 'adk_session_id' in created_channels[guild_id][channel_id]:
        adk_session_id = created_channels[guild_id][channel_id]['adk_session_id']
        user_id = str(message.author.id)

        runner = Runner(
            agent=adk_agent,
            app_name="DiscordBot",
            session_service=session_service_stateful,
        )

        new_message = types.Content(
            role="user", parts=[types.Part(text=message.content)]
        )

        try:
            response_text = ""
            async with message.channel.typing():
                for event in runner.run(user_id=user_id, session_id=adk_session_id, new_message=new_message):
                    if event.is_final_response():
                        if event.content and event.content.parts:
                            response_text = event.content.parts[0].text
                            break # Exit loop after getting final response

            if response_text:
                await message.channel.send(response_text)
        except Exception as e:
            print(f"Error running ADK agent: {e}")
            await message.channel.send("An error occurred while processing your request.")

    # Allow other commands to be processed
    await bot.process_commands(message)

@bot.command()
async def sidebar(ctx):
    guild = ctx.guild
    existing_channel_names = [channel.name for channel in guild.text_channels]
    attempts = 0
    max_attempts = len(ADJECTIVES) * len(NAMES)

    while True:
        if attempts >= max_attempts:
            await ctx.send("All AI channels are currently busy. Please try again later.")
            return
        
        adjective = random.choice(ADJECTIVES)
        name = random.choice(NAMES)
        channel_name = f"{adjective}-{name}".lower()
        
        if channel_name not in existing_channel_names:
            break
        attempts += 1
    
    category_obj = discord.utils.get(guild.categories, name='AIs')
    if not category_obj:
        category_obj = await guild.create_category('AIs')
    
    channel = await guild.create_text_channel(channel_name, category=category_obj)
    message = await ctx.send(f'Sidebar created in <#{channel.id}>')
    
    # Create a new ADK session for this channel
    user_id = str(ctx.author.id) # Use Discord user ID as ADK user ID
    session_id = str(uuid.uuid4()) # Generate a unique session ID for ADK

    initial_state = {
        "user": ctx.author.display_name,
        "channel_name": channel.name,
        "user_preferences": "The user is interacting via Discord.",
    }

    adk_session = await session_service_stateful.create_session(
        app_name="DiscordBot", # A consistent app name for all sessions
        user_id=user_id,
        session_id=session_id,
        state=initial_state,
    )

    async with channel_lock:
        if guild.id not in created_channels:
            created_channels[guild.id] = {}
        created_channels[guild.id][channel.id] = {
            'original_channel_id': ctx.channel.id,
            'message_id': message.id,
            'sender_message_id': ctx.message.id,
            'adk_session_id': adk_session.id
        }

@bot.command()
async def exit(ctx):
    channel = ctx.channel
    guild = ctx.guild
    if channel.category and channel.category.name == 'AIs':
        async with channel_lock:
            if guild.id in created_channels and channel.id in created_channels[guild.id]:
                channel_info = created_channels[guild.id].pop(channel.id)
                # ADK session cleanup is implicit as the reference is removed from created_channels
                try:
                    original_channel = bot.get_channel(channel_info['original_channel_id'])
                    if original_channel:
                        message = await original_channel.fetch_message(channel_info['message_id'])
                        await message.delete()
                except discord.NotFound:
                    print(f"Message {channel_info['message_id']} not found in channel {channel_info['original_channel_id']}.")
                except discord.Forbidden:
                    print(f"Bot does not have permissions to delete message {channel_info['message_id']} in channel {channel_info['original_channel_id']}.")
        await channel.delete()
    else:
        await ctx.send("This command can only be used in a channel under the 'AIs' category.", delete_after=10)

@bot.command()
async def clear(ctx):
    await ctx.send("Are you sure you want to clear all messages in this channel? (yes/no)", delete_after=30)

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']

    try:
        msg = await bot.wait_for('message', check=check, timeout=30.0)
    except asyncio.TimeoutError:
        await ctx.send("Clear command timed out.")
    else:
        if msg.content.lower() == 'yes':
            await ctx.channel.purge()
        else:
            await ctx.send("Clear command cancelled.")

bot.run(DISCORD_TOKEN)
