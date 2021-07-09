import asyncio
from contextlib import suppress

import discord
from discord.ext import commands

import checks
import utils
from checks import NoKaraokeChannel


class DiscordBot(commands.Bot):

    def __init__(self, **options):
        self.cfg = utils.Config(self)
        super().__init__(self.cfg.get('core.prefix'), **options)


def init():
    bot = DiscordBot()
    bot.remove_command('help')

    extensions = bot.cfg.get('core.InitialExtensions')
    for extension in extensions:
        bot.load_extension(f'cogs.{extension}')

    @bot.event
    async def on_ready():
        print('The bot is ready to use!')
        print(f'Invite: {discord.utils.oauth_url(bot.user.id)}&permissions=8')

    @bot.event
    async def on_command_error(ctx, error):

        ignored = (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument)

        error = getattr(error, 'original', error)
        if isinstance(error, ignored):
            return

        if isinstance(error, NoKaraokeChannel):
            with suppress(discord.NotFound, discord.Forbidden):
                await ctx.message.delete()
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'This channel is no karaoke channel.'
            return await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.MissingPermissions):
            with suppress(discord.NotFound, discord.Forbidden):
                await ctx.message.delete()
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'This command is admin only.'
            return await ctx.send(embed=embed, delete_after=15)
        elif isinstance(error, commands.NoPrivateMessage):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'This command only works on a server.'
            return await ctx.send(embed=embed)
        # raise error

    return bot


if __name__ == '__main__':
    bot = init()
    loop = asyncio.get_event_loop()

    loop.run_until_complete(bot.run(bot.cfg.get('core.Token')))

    # Coded by Focus™#0001
    # don't forget to give me credits

