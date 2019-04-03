import discord
from discord.ext import commands

from io import BytesIO

MAILBOX = 562757075537756171
#MAILBOX = 482598997966585866

class Mail:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(lambda ctx:isinstance(ctx.channel, discord.DMChannel))
    async def submit(self, ctx, *, mail):
        """Submit a problem to the mailbox
        Works in DMs only.
        Abuse this and be blacklisted
        """
        message = f"Submission from {ctx.author}. Reply with `{ctx.author.id}`.\n\n"
        message += mail
        channel = self.bot.get_channel(MAILBOX)
        if channel is None:
            return await ctx.send("Oops, I can't find the mailbox")

        await self.send_message(channel, message, ctx.message.attachments)

    @commands.command()
    @commands.check(lambda ctx: ctx.channel.id==MAILBOX)
    async def reply(self, ctx, user: discord.User, *, mail):
        """Reply to a user"""
        message = f"Reply from curators\n\n"
        message += mail

        await self.send_message(user, message, ctx.message.attachments)

    async def send_message(self, dest, message, files):
        limit = 2000
        if len(message) > limit:
            messages = (message[:limit-200], message[limit:] + "\n\n*Yeah screw message splitting.*")
        else:
            messages = (message,)


        if len(messages) > 1:
            await dest.send(messages[0])

        attachments = []
        for attachment in files:
            f = BytesIO()
            await attachment.save(f)
            attachments.append((f, attachment.filename))

        attachments = [discord.File(a[0], a[1]) for a in attachments]
        await dest.send(messages[-1], files=attachments)




def setup(bot):
    bot.add_cog(Mail(bot))