import discord
from discord.ext import commands

import checks


class Karaoke(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.current_users = {}
        self.locked = False

    @commands.command(name='help')
    @checks.is_karaoke_channel()
    @commands.guild_only()
    async def _help(self, ctx):
        embed = discord.Embed(colour=discord.Colour.dark_teal())
        embed.title = 'Karaoke Help'
        embed.description = '{prefix}queue **-** Show the current karaoke queue.\n' \
                            '{prefix}join **-** Join a karaoke queue.\n' \
                            '{prefix}leave **-** Leave a karaoke queue.\n' \
                            '{next}next **-** Select the next user in queue.\n' \
                            \
                            'Admin Commands.\n' \
                            \
                            '{prefix}channel add|remove **-** add or remove karaoke queue channel.\n' \
                            '{prefix}clear **-** Clear the current queue.\n' \
                            '{prefix}remove [user] **-** Removes the mentioned user from the queue.\n' \
                            '{prefix}add [user] **-** Add the mentioned user from the queue.\n' \
                            '{prefix}swap [user1] [user2] **-** Swaps the Mentioned users on the queue.\n' \
                            '{prefix}lock **-** lock or unlock the command for the queue.\n' \
                            'need help? kindly DM Euskara#0001'
        embed.set_footer(text='The Camp™')
        await ctx.send(embed=embed)

    @commands.command(name='queue')
    @checks.is_karaoke_channel()
    @commands.guild_only()
    async def _queue(self, ctx):
        embed = discord.Embed()
        embed.title = 'Karaoke Queue'
        embed.set_footer(text='karaoke queue')
        if ctx.channel not in self.current_users:
            embed.colour = discord.Colour.gold()
            embed.description = 'The queue is currently empty.'
            return await ctx.send(embed=embed)

        members = self.current_users[ctx.channel]
        formatted_members = []
        for i, member in enumerate(members):
            member: discord.Member
            f = lambda x: f'{member}{f"({member.nick})" if member.nick else ""}'
            if i == 0:
                formatted_members.append(f'**Current turn:** {f(member)}')
                continue
            formatted_members.append(f'**{i}** | {f(member)}')

        embed.colour = discord.Colour.dark_teal()
        embed.description = '\n\n'.join(formatted_members)
        return await ctx.send(embed=embed)

    @commands.command(name='join')
    @checks.is_karaoke_channel()
    @commands.guild_only()
    async def _join(self, ctx):
        if self.locked:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.description = 'The queue is currently locked.'
            embed.set_footer(text='karaoke queue')
            return await ctx.send(embed=embed)
        if ctx.channel not in self.current_users:
            self.current_users[ctx.channel] = []
        if ctx.author in self.current_users[ctx.channel]:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'You are already in the queue.'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)
        self.current_users[ctx.channel].append(ctx.author)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = 'You got successfully added to the queue.'
        embed.set_footer(text='set your footer here')
        return await ctx.send(embed=embed)

    @commands.command(name='leave')
    @checks.is_karaoke_channel()
    @commands.guild_only()
    async def _leave(self, ctx):
        if self.locked:
            embed = discord.Embed(colour=discord.Colour.red())
            embed.description = 'The queue is currently locked.'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)
        if ctx.channel not in self.current_users:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The queue is currently empty'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)
        if ctx.author not in self.current_users[ctx.channel]:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'You are not in the queue.'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)
        if len(self.current_users[ctx.channel]) == 1:
            del self.current_users[ctx.channel]
        else:
            self.current_users[ctx.channel].remove(ctx.author)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = 'You got successfully got removed from the queue.'
        embed.set_footer(text='set your footer here')
        return await ctx.send(embed=embed)

    @commands.command(name='next')
    @checks.is_karaoke_channel()
    @commands.guild_only()
    async def _next(self, ctx):
        if ctx.channel not in self.current_users:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The queue is currently empty'
            embed.set_footer(text='The Camp™')
            return await ctx.send(embed=embed)
        if ctx.author is not self.current_users[ctx.channel][0]:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'Only the current member can execute this command.'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)
        finished_member = self.current_users[ctx.channel].pop(0)
        if len(self.current_users[ctx.channel]) > 0:
            current_member = self.current_users[ctx.channel][0]
            embed = discord.Embed(colour=discord.Colour.green())
            embed.description = f'{finished_member.name} finished.\n\n' \
                                f'**{current_member.name} now it\'s your turn.**'
            embed.set_footer(text='set your footer here')
            return await ctx.send(content=current_member.mention, embed=embed)
        else:
            del self.current_users[ctx.channel]
            embed = discord.Embed(colour=discord.Colour.gold())
            embed.description = f'{finished_member.name} finished.\n\n' \
                                f'**The queue is now empty.**'
            embed.set_footer(text='set your footer here')
            return await ctx.send(embed=embed)

    # Admin Commands
    @commands.command(name='clear')
    @commands.has_permissions(administrator=True)
    @checks.is_karaoke_channel()
    async def _clear(self, ctx):
        if ctx.channel not in self.current_users:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The queue is already empty.'
            return await ctx.send(embed=embed)
        del self.current_users[ctx.channel]
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully cleared the queue.'
        return await ctx.send(embed=embed)

    @commands.command(name='remove')
    @commands.has_permissions(administrator=True)
    @checks.is_karaoke_channel()
    async def _remove(self, ctx, member: discord.Member):
        if ctx.channel not in self.current_users:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The queue is empty.'
            return await ctx.send(embed=embed)
        if member not in self.current_users[ctx.channel]:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The member is not in the queue.'
            return await ctx.send(embed=embed)
        self.current_users[ctx.channel].remove(member)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully removed {member.name} from the queue.'
        return await ctx.send(embed=embed)

    @_remove.error
    async def _remove_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}remove <Member>`.'
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The given argument is no member.'
            return await ctx.send(embed=embed)

    @commands.command(name='add')
    @commands.has_permissions(administrator=True)
    @checks.is_karaoke_channel()
    async def _add(self, ctx, member: discord.Member):
        if ctx.channel not in self.current_users:
            self.current_users[ctx.channel] = []
        if member in self.current_users[ctx.channel]:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The member is already in the queue.'
            return await ctx.send(embed=embed)
        self.current_users[ctx.channel].append(member)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully added {member.name} to the queue.'
        return await ctx.send(embed=embed)

    @_add.error
    async def _add_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}add <Member>`.'
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The given argument is no member.'
            return await ctx.send(embed=embed)

    @commands.command(name='swap')
    @commands.has_permissions(administrator=True)
    @checks.is_karaoke_channel()
    async def _swap(self, ctx, member1: discord.Member, member2: discord.Member):
        if ctx.channel not in self.current_users:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The queue is empty.'
            return await ctx.send(embed=embed)
        for member in [member1, member2]:
            if member not in self.current_users[ctx.channel]:
                embed = discord.Embed(colour=discord.Colour.dark_red())
                embed.description = 'The member is not in the queue.'
                return await ctx.send(embed=embed)

        pos1 = self.current_users[ctx.channel].index(member1)
        pos2 = self.current_users[ctx.channel].index(member2)
        self.current_users[ctx.channel].remove(member1)
        self.current_users[ctx.channel].remove(member2)
        self.current_users[ctx.channel].insert(pos2, member1)
        self.current_users[ctx.channel].insert(pos1, member2)

        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully switched {member1.name} and {member2.name} position.'
        return await ctx.send(embed=embed)

    @_swap.error
    async def _swap_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}swap <Member1> <Member2>`.'
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The given argument is no member.'
            return await ctx.send(embed=embed)

    @commands.command(name='prefix')
    @commands.has_permissions(administrator=True)
    async def _prefix(self, ctx, prefix: str):
        ctx.bot.cfg.set('core.token', prefix)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully set prefix.\n' \
                            f'> Prefix: `{prefix}`'
        return await ctx.send(embed=embed)

    @_prefix.error
    async def _prefix_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}prefix <Prefix>`.'
            return await ctx.send(embed=embed)

    @commands.command(name='lock')
    @commands.command(administrator=True)
    async def _lock(self, ctx):
        if self.locked:
            self.locked = False
            embed = discord.Embed(colour=discord.Colour.green())
            embed.description = f'Successfully unlocked commands.'
            return await ctx.send(embed=embed)
        else:
            self.locked = True
            embed = discord.Embed(colour=discord.Colour.green())
            embed.description = f'Successfully locked commands.'
            return await ctx.send(embed=embed)

    @commands.group(name='channel', invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def _channel(self, ctx):
        channel_ids = ctx.bot.cfg.get('karaoke.channels')
        channels = [ctx.bot.get_channel(cid) for cid in channel_ids]
        formatted_channels = [c.mention if c else 'Not Found' for c in channels]
        embed = discord.Embed(colour=discord.Colour.green())
        embed.title = 'Karaoke Channels'
        embed.description = ', '.join(formatted_channels)
        embed.add_field(name='**Help**',
                        value=f'`{ctx.prefix}channel add <Channel>` - Add a karaoke channel\n'
                              f'`{ctx.prefix}channel remove <Channel>` - Remove a karaoke channel')
        return await ctx.send(embed=embed)

    @_channel.command(name='add')
    async def _channel_add(self, ctx, channel: discord.TextChannel):
        channel_ids = ctx.bot.cfg.get('karaoke.channels')
        if channel.id in channel_ids:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'The channel is already a karaoke channel.'
            return await ctx.send(embed=embed)
        channel_ids.append(channel.id)
        ctx.bot.cfg.set('karaoke.channels', channel_ids)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully added {channel.mention}.'
        return await ctx.send(embed=embed)

    @_channel_add.error
    async def _channel_add_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}channel add <Channel>`.'
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The given argument is no channel.'
            return await ctx.send(embed=embed)

    @_channel.command(name='remove')
    async def _channel_remove(self, ctx, channel: discord.TextChannel):
        channel_ids = ctx.bot.cfg.get('karaoke.channels')
        if channel.id not in channel_ids:
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'The channel is no karaoke channel.'
            return await ctx.send(embed=embed)
        channel_ids.remove(channel.id)
        ctx.bot.cfg.set('karaoke.channels', channel_ids)
        embed = discord.Embed(colour=discord.Colour.green())
        embed.description = f'Successfully removed {channel.mention}.'
        return await ctx.send(embed=embed)

    @_channel_remove.error
    async def _channel_remove_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = f'Please use `{ctx.prefix}channel remove <Channel>`.'
            return await ctx.send(embed=embed)
        elif isinstance(error, commands.BadArgument):
            embed = discord.Embed(colour=discord.Colour.dark_red())
            embed.description = 'The given argument is no channel.'
            return await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Karaoke(bot))
