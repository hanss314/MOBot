import asyncio
import discord
import time
import bisect

from discord.ext import commands

class Job:
    def __init__(self, ctx, role, time, members, add):
        self.ctx = ctx
        self.role = role
        self.time = time
        self.members = members
        self.add = add

    async def run(self):
        for member in self.members:
            try:
                func = member.add_roles if self.add else member.remove_roles
                await func(self.role)
            except discord.Forbidden:
                await self.ctx.send(
                    f'{self.ctx.author.mention} I actually can\'t '
                    f'{"add" if self.add else "remove"} {self.role}.'
                )
                return
            except discord.HTTPException:
                pass

    def __lt__(self, other):
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time

    def __str__(self):
        s = "Add **{}** to " if self.add else "Remove **{}** from "
        s = s.format(str(self.role))
        username = lambda x: x.name
        if len(self.members) <= 2:
            s += ', '.join(map(username, self.members))
        else:
            s += ', '.join(map(username, self.members[:2])) + \
                 f', {len(self.members) - 2} others...'

        s += f' in {int(self.time - time.time())} seconds'
        return s


class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jobs = []
        self.loop = False

    async def check_loop(self):
        while self.jobs:
            print('Checking')
            while self.jobs and self.jobs[0].time <= time.time():
                print('Running job!')
                await self.jobs.pop(0).run()

            await asyncio.sleep(5)

        self.loop = False

    async def start_loop(self):
        if not self.loop:
            self.loop = True
            await self.check_loop()

    @commands.command(name='give-after', aliases=['give'], hidden=True)
    @commands.has_role(558563826891751425)
    async def give_after(self, ctx, role: discord.Role, seconds: int,
                      *members: discord.Member):
        """Give a list of members a role in seconds amount of time"""
        job = Job(ctx, role, time.time()+seconds, members, True)
        bisect.insort(self.jobs, job)
        await ctx.send("Job enqueued. Use `m.jobs` to see all jobs")
        await self.start_loop()

    @commands.command(name='remove-after', aliases=['remove'], hidden=True)
    @commands.has_role(558563826891751425)
    async def remove_after(self, ctx, role: discord.Role, seconds: int,
                      *members: discord.Member):
        """Remove a role members after a specified amount of seconds"""
        job = Job(ctx, role, time.time() + seconds, members, False)
        bisect.insort(self.jobs, job)
        await ctx.send("Job enqueued. Use `m.jobs` to see all jobs")
        await self.start_loop()

    @commands.command(name='apply-for', aliases=['apply'], hidden=True)
    @commands.has_role(558563826891751425)
    async def apply_for(self, ctx, role: discord.Role, seconds: int,
                           *members: discord.Member):
        """Apply a role to members for a specified amount of seconds"""
        job = Job(ctx, role, time.time(), members, True)
        await job.run()
        job = Job(ctx, role, time.time() + seconds, members, False)
        bisect.insort(self.jobs, job)
        await ctx.send("Job enqueued. Use `m.jobs` to see all jobs")
        await self.start_loop()

    @commands.command(name='jobs', hidden=True)
    @commands.has_role(558563826891751425)
    async def view_jobs(self, ctx):
        """View all role management jobs"""
        s = "**Jobs**\n"
        for n, job in enumerate(self.jobs):
            s += f"{n+1}: {str(job)}\n"

        await ctx.send(s)

    @commands.command(name="remove-job", aliases=['remjob'], hidden=True)
    @commands.has_role(558563826891751425)
    async def remove_job(self, ctx, job: int):
        """Remove a job. See all jobs with `m.jobs`"""
        if 0 < job <= len(self.jobs):
            self.jobs.pop(job-1)
            await ctx.send("Job removed")
        else:
            await ctx.send("That job does not exist")


def setup(bot):
    bot.add_cog(Roles(bot))
