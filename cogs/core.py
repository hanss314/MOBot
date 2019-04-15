import asyncio
import subprocess
import inspect

import discord
from discord.ext import commands

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx, command:str=None):
        """Get a list of commands or help on a particular command"""
        if command is None:
            message = "**List of commands**\n\n"
            for name in self.bot.cogs:
                if hasattr(self.bot.cogs[name], '_hidden'): continue
                cog = f"*{name}*\n"
                commands = ''
                for cmd in sorted(self.bot.get_cog_commands(name), key=lambda c:c.name):
                    if cmd.hidden : continue
                    brief = cmd.brief
                    if brief is None and cmd.help is not None:
                        brief = cmd.help.split('\n')[0]

                    commands += f"`{ctx.prefix}{cmd.name}` - {brief}\n"

                if commands:
                    message += cog+commands+'\n'

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

    @commands.command(hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def blacklist(self, ctx, user: discord.Member):
        """Blacklist a user"""
        if user.id in self.bot.blacklist:
            return await ctx.send(f"{user} is already blacklisted!")

        self.bot.blacklist.append(user.id)
        return await ctx.send(f"{user} has been blacklisted")

    @commands.command(hidden=True)
    @commands.has_permissions(manage_guild=True)
    async def unblacklist(self, ctx, user: discord.Member):
        """Unblacklist a user"""
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def update(self, ctx):
        """Updates the bot from git"""
        await ctx.send(':radioactive: Warning! :radioactive: Warning! :radioactive: Pulling from git!')

        process = await asyncio.create_subprocess_exec(
            'git', 'pull', stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        stdout = stdout.decode().splitlines()
        stdout = '\n'.join('+ ' + i for i in stdout)
        stderr = stderr.decode().splitlines()
        stderr = '\n'.join('- ' + i for i in stderr)

        await ctx.send('`Git` response: ```diff\n{}\n{}```'.format(stdout, stderr))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, cog=''):
        """Reloads an extension"""
        try:
            ctx.bot.reload_extension(cog)
        except commands.ExtensionFailed as e:
            await ctx.send(f'Failed to load: `{cog}`\n```py\n{e.original}\n```')
        else:
            await ctx.send(f'Reloaded cog {cog} successfully')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def eval(self, ctx, *, code: str):
        '''Evaluates code'''

        env = {
            'ctx': ctx,
            'bot': ctx.bot,
            'guild': ctx.guild,
            'author': ctx.author,
            'message': ctx.message,
            'channel': ctx.channel
        }
        env.update(globals())

        try:
            result = eval(code, env)
            if inspect.isawaitable(result):
                result = await result

            colour = 0x00FF00
        except Exception as e:
            result = type(e).__name__ + ': ' + str(e)
            colour = 0xFF0000

        embed = discord.Embed(colour=colour, title=code, description='```py\n{}```'.format(result))
        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.remove_command('help')
    bot.add_cog(Core(bot))