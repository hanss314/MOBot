import discord
from discord.ext import commands

class Core:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command:str=None):
        """Get a list of commands or help on a particular command"""
        if command is None:
            message = "**List of commands**\n\n"
            for cmd in sorted(self.bot.all_commands.values(), key=lambda c:c.name):
                if cmd.hidden : continue
                try:
                    if not (await cmd.can_run(ctx)): continue
                except commands.CheckFailure: continue

                brief = cmd.brief
                if brief is None and cmd.help is not None:
                    brief = cmd.help.split('\n')[0]

                message += f"`{ctx.prefix}{cmd.name}` - {brief}\n"

        else:
            command = command.lstrip(ctx.prefix).lower()
            if command not in self.bot.all_commands:
                return await ctx.send('Command not found.')

            cmd = self.bot.all_commands[command]
            params = list(cmd.clean_params.items())
            p_str = ''
            for p in params:
                if p[1].default == p[1].empty:
                    p_str += f' <{p[0]}>'
                else:
                    p_str += f' [{p[0]}]'

            message = f"`{ctx.prefix}{cmd.name}{p_str}` \n{cmd.help}"

        try:
            await ctx.author.send(message)
        except Exception:
            return await ctx.send(message)

        try:
            await ctx.message.add_reaction('📬')
        except Exception: pass

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def blacklist(self, ctx, user: discord.Member):
        """Blacklist a user"""
        if user.id in self.bot.blacklist:
            return await ctx.send(f"{user} is already blacklisted!")

        self.bot.blacklist.append(user.id)
        return await ctx.send(f"{user} has been blacklisted")

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unblacklist(self, ctx, user: discord.Member):
        """Blacklist a user"""
        if user.id not in self.bot.blacklist:
            return await ctx.send(f"{user} is not blacklisted!")

        self.bot.blacklist.remove(user.id)
        return await ctx.send(f"{user} has been unblacklisted")

    @blacklist.after_invoke
    @unblacklist.after_invoke
    async def save_blacklist(self, _):
        with open(f"config/{self.bot.config['blacklist']}", 'w') as listfile:
            for uid in self.bot.blacklist:
                listfile.write(str(uid)+'\n')


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Core(bot))