# Mini-Jukebox
# jukebox_checks.py
# Written by blueberry et al., 2022
# https://github.com/StardewValleyDiscord/mini-jukebox

"""
Contents:
    Check errors
    Check functions
"""
from lib2to3.fixes.fix_input import context
from tokenize import maybe
from typing import Union, List

import discord
from discord.ext import commands
from discord.ext.commands import Context
from discord.ui import View

import config
import strings
from jukebox_impl import jukebox


# Check errors


class CheckFailureQuietly(commands.CheckFailure):
    """
    Override for check failure error for specific error handling.
    """
    pass


# Check functions


def _check_roles(user: Union[discord.User, discord.Member], role_ids: List[int]) -> bool:
    """
    Check roles
    Source: StardewValleyDiscord - Autumn2022
    :param user: A user or member object, where a user that is not a member is ensured not to have any roles.
    :param role_ids: A list of role IDs to check for.
    :return: Whether a user has any of the roles in a given list.
    """
    return (isinstance(user, discord.Member)
            and len(role_ids) > 0 and len([r for r in user.roles if r.id in role_ids]) > 0)
async def is_admin(ctx: Context, send_message: bool = True) -> bool:
    facts = _check_roles(ctx.author, [config.ROLE_ADMIN])
    if ctx.author.id == config.USER_CHATHAM:
        return True
    if not facts and send_message:
        msg = strings.get("error_command_role_permissions")
        await ctx.reply(content=msg)
    return facts

async def user_id_is_admin(userid):
    """ ok like is_admin wants a ctx and i don't have ctx in a interaction so im using user id instead
    also because im too lazy to get user id as a real user im just checking if its MY user id bc i cbf
    checking other admin rights"""
    if userid == config.USER_CHATHAM:
        return True

async def createView(viewList: dict):
    view: discord.ui.View = View()
    for i in viewList.values():
        view.add_item(i)
    return view



async def is_not_blacklisted(ctx: Context, send_message: bool = False) -> bool:
    facts = _check_roles(ctx.author, [config.ROLE_BLACKLISTED])
    if facts is True:
        return False
    else:
        return True

async def is_dj(ctx: Context, send_message: bool = True) -> bool:
    facts = _check_roles(ctx.author, [config.ROLE_DJ])
    if facts is False or not is_admin(ctx):
        msg = strings.get("error_command_role_permissions")
        if send_message:
             await ctx.reply(content=msg)
    return facts

async def is_voice_only(ctx: Context, send_message: bool = True) -> bool:
    # Filter voice-only command uses by users currently in the voice channel
    facts = jukebox.is_in_voice_channel(member=ctx.author) or _check_roles(ctx.author, [config.ROLE_ADMIN])
    if not facts and send_message:
        # Users can only play the jukebox if they're in the voice channel
        msg = strings.get("error_command_voice_only").format(
            jukebox.bot.get_channel(config.CHANNEL_VOICE).mention)
        await ctx.reply(content=msg)
    return facts

async def is_channel_ok(ctx: Context) -> bool:
    return ctx.channel.id == config.CHANNEL_TEXT \
       or await is_admin(ctx=ctx, send_message=False)

async def is_looping_enabled(ctx: Context) -> bool:
    return config.PLAYLIST_LOOPING

async def is_pausing_enabled(ctx: Context) -> bool:
    return config.PLAYLIST_PAUSING
