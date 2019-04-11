import asyncio
import discord

from discord.ext import commands


class Roles:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='give-after', aliases=['give'], hidden=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def give_after(self, ctx, role: discord.Role, seconds: int,
                      *members: discord.Member):
        """Give a list of members a role in seconds amount of time"""
        await asyncio.sleep(seconds)
        for member in members:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                await ctx.send(f'{ctx.author.mention} I actually can\'t add {role}.')
                return
            except discord.HTTPException:
                pass

    @commands.command(name='remove-after', aliases=['remove'], hidden=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def remove_after(self, ctx, role: discord.Role, seconds: int,
                      *members: discord.Member):
        """Remove a role members after a specified amount of seconds"""
        await asyncio.sleep(seconds)
        for member in members:
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                await ctx.send(f'{ctx.author.mention} I actually can\'t remove {role}.')
                return
            except discord.HTTPException:
                pass

    @commands.command(name='apply-for', aliases=['apply'], hidden=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def apply_for(self, ctx, role: discord.Role, seconds: int,
                           *members: discord.Member):
        """Apply a role to members for a specified amount of seconds"""
        for member in members:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                await ctx.send(f'{ctx.author.mention} I actually can\'t add {role}.')
                return
            except discord.HTTPException:
                pass
        await asyncio.sleep(seconds)
        for member in members:
            try:
                await member.remove_roles(role)
            except discord.Forbidden:
                await ctx.send(f'{ctx.author.mention} I actually can\'t remove {role}.')
                return
            except discord.HTTPException:
                pass


def setup(bot):
    bot.add_cog(Roles(bot))
