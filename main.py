# Mini-Jukebox
# main.py
# Written by blueberry et al., 2022
# https://github.com/StardewValleyDiscord/mini-jukebox

"""
Contents:
    Logging
    Bot definition
        MusicBot
            Help commands
            Init
            Bot events
            Bot utilities
    Utilities
    Init
    Runtime events
    Global commands
    Startup
    TEEEEEEEEEEEEEEEEST
"""

import asyncio
import logging
import os
import shutil
from datetime import datetime
from logging.handlers import RotatingFileHandler
from importlib import reload
from typing import Optional

import discord
import psutil
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context, HelpCommand

import DISCORD_TOKEN
import config
import db
import err
import jukebox_commands
import strings
from jukebox_checks import is_admin, CheckFailureQuietly, is_channel_ok
from jukebox_impl import jukebox
from jukebox_commands import ensure_voice



# Utilities


def _clear_temp_folders() -> None:
    try:
        fp: str = config.LOG_DIR
        if os.path.exists(fp):
            shutil.rmtree(fp)
        os.mkdir(fp)
    except Exception as error:
        err.log(error)


# Logging


_clear_temp_folders()
if config.LOGGING_FILE:
    logger: logging.Logger = logging.getLogger("discord")
    handler: RotatingFileHandler = RotatingFileHandler(
        filename=config.LOG_PATH,
        encoding="utf-8",
        maxBytes=int(config.LOG_SIZE_MEBIBYTES * 1024 * 1024),
        backupCount=config.LOG_BACKUP_COUNT
    )
    formatter: logging.Formatter = logging.Formatter(
        fmt=strings.get("log_format"),
        datefmt=strings.get("datetime_format_log")
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)


# Bot definition


class MusicBot(Bot):
    """
    Bot used for running a jukebox service in a given voice channel, taking commands from a separate text channel.
    """

    # Help commands

    class MusicHelpCommand(HelpCommand):
        """
        Override of HelpCommand to redirect to some default help docs.
        """

        async def send_bot_help(self, ctx: Context) -> None:
            await self._send_help()

        async def send_cog_help(self, cog: commands.Cog) -> None:
            await self._send_help()

        async def send_group_help(self, group: commands.Group) -> None:
            await self._send_help()

        async def send_command_help(self, command: commands.Command) -> None:
            await self._send_help()

        async def _send_help(self) -> None:
            """
            Sends a basic help prompt.
            """
            text_channel = self.get_destination()
            await text_channel.send(strings.get("info_help").format(
                text_channel.mention,
                strings.emoji_pin))

    # Init

    def __init__(self) -> None:
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            intents=config.DISCORD_INTENTS,
            description=strings.get("client_description"),
            case_insensitive=True,
            allowed_mentions=discord.AllowedMentions.none())
        self.help_command = self.MusicHelpCommand()
        self.db = db
        self.start_time = datetime.now()

    # Bot events

    async def setup_hook(self) -> None:
        """
        Inherited from Client. Called once internally after login. Used to load all initial command extensions.
        """
        # Load database
        db.setup()
        # Load required extensions
        await self.load_extension(name=jukebox_commands.__name__)
        jukebox.bot = self

    async def on_ready(self) -> None:
        """
        Inherited from Client. Called once internally after all setup. Used only to log notice.
        """
        msg = strings.get("log_console_client_ready").format(
            self.user.name,
            self.user.discriminator,
            self.user.id)
        print(msg)
        await ensure_voice()

        if config.LOGGING_CHANNEL:
            channel = self.get_channel(config.CHANNEL_LOG)
            msg = strings.get("log_channel_client_ready").format(
                self.user.name,
                self.user.discriminator,
                self.user.id,
                strings.emoji_connection)
            await channel.send(content=msg)

    async def on_command(self, ctx: Context) -> None:
        """
        Additional behaviours on commands used to vet or audit commands.
        """
        # Log all used jukebox commands for auditing
        await self.log_command(ctx=ctx)

    async def on_command_error(self, ctx: Context, error: Exception) -> None:
        """
        Additional behaviours on errors using commands to either suppress, react, or reply.
        """
        # Add a reaction to posts with unknown commands or invalid uses
        msg: Optional[str] = None
        reaction: Optional[str] = None
        try:
            if isinstance(error, CheckFailureQuietly) or not await is_channel_ok(ctx=ctx):
                # Quietly suppress certain failed command checks
                return
            elif isinstance(error, commands.CheckFailure):
                # Suppress failed command checks
                reaction = strings.emoji_error
            elif isinstance(error, commands.errors.CommandNotFound):
                # Suppress failed command calls
                reaction = strings.emoji_question
            elif isinstance(error, commands.errors.BadArgument):
                # Suppress failed command parameters
                reaction = strings.emoji_error
            else:
                # Notify and log other errors
                reaction = strings.emoji_error
                err.log(error)

                if config.LOGGING_CHANNEL:
                    # Send error message in log channel
                    error_msg: str = strings.get("log_channel_command_error").format(
                        ctx.author.name,
                        ctx.author.discriminator,
                        ctx.author.id,
                        ctx.channel.mention,
                        ctx.message.jump_url,
                        strings.emoji_error)
                    log_channel: discord.TextChannel = ctx.guild.get_channel(config.CHANNEL_LOG)
                    error_file: discord.File = err.traceback_as_file(error.original)

                    # Send error with stack trace as message attachment
                    await log_channel.send(content=error_msg, file=error_file)

                if isinstance(error, TimeoutError):
                    # Send message on connection timeout
                    msg = strings.get("info_connection_timed_out").format(strings.emoji_connection)
                else:
                    # Rethrow other errors
                    raise error
        finally:
            if msg:
                await ctx.reply(content=msg)
            if reaction:
                await ctx.message.add_reaction(reaction)

    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState) -> None:
        """
        Update bot state based on listeners in voice channel.
        """
        # Stop playing music and leave the voice channel if all other users have disconnected
        if member.guild.voice_client and before.channel and before.channel.id == config.CHANNEL_VOICE and len(before.channel.members) < 2:
            jukebox.stop()
            await member.guild.voice_client.disconnect(force=True)
            if member.id == bot.user.id:
                if before.channel is None and after.channel is not None:
                    await bot.get_channel(config.CHANNEL_LOG).send("Joined voicechat.")
                if before.channel is not None and after.channel is None:
                    await bot.get_channel(config.CHANNEL_LOG).send("Left voicechat.")
        if not member.guild.voice_client and len(after.channel.members) >= 1 and after.channel.id == config.CHANNEL_VOICE:
            await ensure_voice()

    def reload_strings(self) -> None:
        """
        Reloads all text strings from data file for bot commands and interactions.
        """
        reload(strings)

    # Bot utilities

    async def log_command(self, ctx: Context) -> None:
        """
        Log commands-used to the console and/or logging channel for auditing.
        """
        if await is_valid_command_use(ctx=ctx):
            user = ctx.message.author
            log_msg: str = strings.get("log_console_command_used").format(
                    user.name,
                    user.discriminator,
                    user.id,
                    ctx.message.content)
            if config.LOGGING_CONSOLE:
                print(log_msg)
            if config.LOGGING_FILE:
                logging.getLogger("discord").debug(log_msg)
            if config.LOGGING_CHANNEL:
                emoji = await commands.EmojiConverter().convert(ctx=ctx, argument=strings.get("emoji_id_jukebox"))
                log_msg = strings.get("log_channel_command_used").format(
                    user.name,
                    user.discriminator,
                    user.id,
                    ctx.channel.mention,
                    ctx.message.content,
                    emoji)
                await self.get_channel(config.CHANNEL_LOG).send(content=log_msg)


# Init

bot = MusicBot()
"""Main instance of the bot."""


# Global commands


@bot.check
async def is_valid_command_use(ctx: Context) -> bool:
    """
    Global check to determine whether a given command should be processed.
    """
    # Ignore commands from bots
    is_bot: bool = ctx.author.bot

    # Ignore commands from channels other than the designated text channel (except commands used by admins)
    is_channel: bool = await is_channel_ok(ctx=ctx)

    # Ignore commands while commands are blocked (except commands used by admins)
    is_blocked: bool = bot.get_cog(config.COG_COMMANDS).is_blocking_commands \
        and not await is_admin(ctx=ctx, send_message=False)

    if is_bot or not is_channel or is_blocked:
        raise CheckFailureQuietly()

    return True

# chatham stuff

@bot.event
async def on_member_update(before, after):
    entry: db.DBUser = bot.db.get_user(user_id=after.id)
    role_timeout = after.guild.get_role(config.ROLE_IN_TIMEOUT)  # Retrieve the role using its ID
    if role_timeout in after.roles and role_timeout not in before.roles:
        # User just got the ROLE_TIMECOUNT role
        entry.in_timeout = 'True'
    elif role_timeout not in after.roles and role_timeout in before.roles:
        # User just lost the ROLE_TIMECOUNT role
        entry.in_timeout = 'False'
    bot.db.update_user(entry=entry)


@bot.event
async def on_member_join(member):
    """
    Event triggered when a member joins the server. Assigns the timeout role
    if their 'inTimeout' field in USERDATA is true.
    """
    entry: db.DBUser = bot.db.get_user(user_id=member.id)
    role_timeout = member.guild.get_role(config.ROLE_IN_TIMEOUT)  # Retrieve the timeout role using its ID
    if entry.in_timeout == 'True':  # Check if `inTimeout` is true
        if role_timeout:
            await member.add_roles(role_timeout)
            await member.guild.get_channel(config.CHANNEL_TIMEOUT).send(f"LMFAO!! this IDIOT <@{member.id}> just tired leaving & rejoing to evade the timeout ")

@bot.event
async def on_message(message: discord.Message):
    if message.guild.id == config.GUILD_AGPDS:
        await bot.get_channel(config.CHANNEL_PRIVATE).send(f"#{message.channel.name} `<@{message.author.id}>: {message.content}`")
    if message.channel.id == 1302851483108245525:
        await bot.process_commands(message)
        # Wait for 30 seconds (300 seconds)
        await asyncio.sleep(300)
        try:
            if not message.pinned:
                await message.delete()
            else:
                print(f"dont delete the pinned message!")

        except discord.Forbidden:
            print(f"Bot does not have permission to delete messages in {message.channel.name}")
        except Exception as e:
            print(f"Error deleting message: {e}")

@tasks.loop(seconds=60)
async def update_cpu():
    try:
        await bot.get_channel(config.CHANNEL_TEXT).edit(topic=f'CPU Usage: {psutil.cpu_percent()}%')
    except Exception as e:
        print(e)

# Discord.py boilerplate
async def main():
    async with bot:
        print(config.COMMAND_PREFIX)
        await bot.start(DISCORD_TOKEN.TOKEN_DISCORD)


asyncio.run(main=main())

