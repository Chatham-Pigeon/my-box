# Mini-Jukebox
# config.py
# Written by blueberry et al., 2022
# https://github.com/StardewValleyDiscord/mini-jukebox

"""
Contents:
    Runtime
    Bot
    Tokens
    Logging
    Discord
    FFMPEG
    Jukebox
    Lyrics
    YTDL
"""

import os

import json
from typing import List

import discord
import yt_dlp


# Runtime

TEMP_DIR: str = "temp"
"""Relative path to temporary folder used to store cached media data."""
LOG_DIR: str = "logs"
"""Relative path to temporary folder used to store session logs."""
CONFIG_PATH: str = "meow?"
"""Relative path to data file used for bot configuration."""
STRINGS_PATH = "assets/strings.json"
"""Relative path to data file used for logging, formatting, reply, and flavour strings."""
PINS_PATH = "assets/pins.json"
"""Relative path to data file used for pinned message contents in text channel."""
DATABASE_PATH: str = "jukebox.db"
"""Relative path to database file used to store usage history."""
LOG_PATH: str = os.path.join(LOG_DIR, "discord.log")
"""Relative path to runtime log files."""

# Bot

COG_COMMANDS: str = "Jukebox Commands"
"""Name of commands cog."""
PACKAGE_COMMANDS: str = "jukebox_commands"
"""Name of commands package."""

# Parse config file


# Tokens

TOKEN_DISCORD: str = "MTMwMjU1NTQ3MzExNTA4Njg3OQ.Gg59qQ.ItYrhOR4R0o0kZFNkwKwu_0ONHmkQu-Pv1ojoI"
"""Token used to run Discord client."""

# Logging

LOG_SIZE_MEBIBYTES: float = 25
LOG_BACKUP_COUNT: int = 2

# Discord

DISCORD_INTENTS: discord.Intents = discord.Intents(
    guilds=True,
    guild_messages=True,
    guild_reactions=True,
    message_content=True,
    members=True,
    emojis=True,
    voice_states=True
)
"""List of allowed and disallowed intents when running Discord client."""

COMMAND_PREFIX: str = "?"
"""Prefix required for all messages sent in command channel."""

ROLE_ADMIN: int = 1232232285722513441
"""Discord role ID for commands and features requiring admin privileges."""
ROLE_TRUSTED: int = 1230678008256401480
"""Discord role ID for commands and features requiring elevated privileges."""
ROLE_DEFAULT: int = 1230678008256401480
"""Discord role ID for commands requiring basic privileges."""
ROLE_LISTEN: int = 1230678008256401480
"""Discord role ID for a role with no privileges."""
ROLE_JUKEBOX: int = 1302579077370089604
"""Discord role ID for bonus flavour role themed around the jukebox."""
ROLE_DJ: int = 1303657331581648916
"""access slightly more important commands"""
ROLE_BLACKLISTED: int = 1303657386371977246
"""no acccess to any commands"""

CHANNEL_VOICE: int = 858670100512768010
"""Discord channel ID for the voice channel used for media playback."""
CHANNEL_TEXT: int = 1302851483108245525
"""Discord channel ID for the text channel used for command interactions."""
CHANNEL_LOG: int = 982041162472915034
"""Discord channel ID used to send status and event logging if configured."""
CHANNEL_BULLETIN: int = 982041162472915034
"""Discord channel ID used to send bulletins and news updates."""

CORO_TIMEOUT: int = 120
"""Duration in seconds before coroutines are timed-out."""
VOICE_TIMEOUT: int = 120
"""Duration in seconds before voice connections are timed-out."""
VOICE_RECONNECT: bool = False
"""Whether to automatically reconnect to voice channels after time-out."""

LOGGING_FILE: bool = False
"""Whether logging usage, events, and tracebacks to file is enabled."""
LOGGING_CHANNEL: bool = True and CHANNEL_LOG is not None
"""Whether a logging channel is configured and enabled for status and commands."""
LOGGING_CONSOLE: bool = False
"""Whether logging status and commands to console is enabled."""

# FFMPEG

FFMPEG_BEFORE_OPTIONS: str = ""
"""Command line parameters for FFMPEG process."""
FFMPEG_OPTIONS: str = "-vn -acodec pcm_s16le -f wav"
"""Command line parameters for FFMPEG media tasks."""

# Jukebox

PLAYLIST_MULTIQUEUE: bool = True
"""Whether multiqueue is enabled, allowing a more even playback of tracks from different users."""
PLAYLIST_STREAMING: bool = True
"""Whether media data will be streamed from external sources, or preloaded and sourced from local drive."""
PLAYLIST_LOOPING: bool = True
"""Whether queues may be toggled to loop their tracks, reappending played tracks."""
PLAYLIST_PAUSING: bool = True
"""Whether queues may be toggled to pause playback until next unpaused."""
TRACK_DURATION_LIMIT: int = 500
"""Duration in seconds for track runtime before being blocked from the queue."""

# Lyrics

TOKEN_LYRICS: str = "ddsadadadasa"
"""Personal access token for lyrics provider."""
LYRICS_LINE_LIMIT: int = 1
"""Maximum number of lines to print to a chat embed."""
LYRICS_CHARACTER_LIMIT: int = 1
"""Maximum number of characters to print to a chat embed."""
LYRICS_SEARCH_TIMEOUT: int = 1
"""Duration in seconds before lyrics provider requests are timed-out."""
LYRICS_VERBOSE: bool = False
"""Whether lyrics provider will use verbose logging."""

# DB

# Packages

PACKAGE_CHECKS: List[str] = []
"""List of package names to list on version checks."""

# YTDL

YTDL_ALLOWED_EXTRACTORS: List[str] = ["youtube.com", "youtu.be", "youtube"]
"""List of permitted media extractors, used to enforce a list of trusted domains to source media from."""
YTDL_OPTIONS = {
    'format': 'worstaudio',         # Choose the best available audio quality
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',    # Use FFmpeg to extract audio
        'preferredcodec': 'mp3',        # Convert audio to mp3 format (can also use 'aac', 'm4a', 'opus', etc.)
        'preferredquality': '192',      # Bitrate for the audio (192k is standard for good quality audio)
    }],
    'noplaylist': True,                 # Ensure only a single video is downloaded, even if it is part of a playlist
    'quiet': True,                      # Suppress the output messages for a cleaner output
    'forcefilename': True,              # Force a filename format that is compatible
    'skip_download': False,             # Stream without saving the file locally
    'default_search': 'ytsearch',       # Set default search to YouTube search if URL is missing
    'source_address': '0.0.0.0',        # Use IPv4 to avoid potential IPv6 issues
    'ratelimit': 500000,  # Limit to 500 KB/s
    'http_chunk_size': 1048576,  # Set to 1 MB chunks


}
"""Flags and values for YTDL connection process."""
YTDL_AMBIGUOUS_ATTEMPTS: int = 10
YTDL_AMBIGUOUS_RESULTS: int = 5

YTDL_OPTIONS["outtmpl"] = YTDL_OPTIONS.get("outtmpl", "%(title)s.%(ext)s")
YTDL_OPTIONS["outtmpl"] = os.path.join(TEMP_DIR, YTDL_OPTIONS["outtmpl"])
yt_dlp.utils.bug_reports_message = lambda: ""
