from discord.ext import commands


def is_karaoke_channel():
    def predicate(ctx: commands.Context):
        if ctx.channel.id not in ctx.bot.cfg.get('karaoke.channels'):
            raise NoKaraokeChannel('This channel is no karaoke channel')
        return True

    return commands.check(predicate)


class NoKaraokeChannel(commands.CheckFailure):
    pass
