import discord
from discord.ext import commands
Cog = commands.Cog

MAILBOX = 562757075537756171
#MAILBOX = 482598997966585866

class Mail(Cog):

    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot: return
        if message.guild is None:
            if message.content.startswith('m.'): return
            m = message
            c = message.channel
            heading = f"Message from {m.author} (`{m.author.id}`)."
            channel = self.bot.get_channel(MAILBOX)
            if channel is None:
                return await channel.send("Oops, I can't find the mailbox")

            await self.send_embed(
                channel, discord.Color.from_rgb(200, 200, 200),
                heading, message.content, message.attachments
            )
            await c.send("Message sent.")
        elif message.channel.id == MAILBOX:
            if not message.content.lower().startswith('r '): return
            m = message
            heading = "Message from the Mathematical Olympiads Server Staff Team"
            try:
                referenced = await m.channel.fetch_message(m.reference.message_id)
                if referenced.author != self.bot.user:
                    return
                user_id = referenced.embeds[0].title.split('`')[-2]
                user = await self.bot.fetch_user(user_id)
            except Exception:
                return
            if user.bot: return
            await self.send_embed(
                user, discord.Color.from_rgb(100, 200, 200),
                heading, m.content[2:], m.attachments
            )
            await m.channel.send(f"Message sent to {user.mention} ({user_id})")


    @commands.command()
    @commands.check(lambda ctx: isinstance(ctx.channel, discord.DMChannel))
    async def problem(self, ctx, *, problem):
        """Submit a problem to the mailbox
        Works in DMs only.
        """
        heading = f"Problem from {ctx.author} (`{ctx.author.id}`)."
        channel = self.bot.get_channel(MAILBOX)
        if channel is None:
            return await ctx.send("Oops, I can't find the mailbox")

        await self.send_embed(
            channel, discord.Color.from_rgb(200, 20, 10),
            heading, problem, ctx.message.attachments
        )
        await ctx.send("Message sent.")

    @commands.command()
    @commands.check(lambda ctx:isinstance(ctx.channel, discord.DMChannel))
    async def solution(self, ctx, problem: int, *, solution):
        """Submit a solution.
        Please specify the problem number
        Works in DMs only.
        """
        heading = f"Solution from {ctx.author} (`{ctx.author.id}`)."
        channel = self.bot.get_channel(MAILBOX)
        if channel is None:
            return await ctx.send("Oops, I can't find the mailbox")

        await self.send_embed(
            channel, discord.Color.from_rgb(10, 200, 10),
            heading, solution, ctx.message.attachments, f"Problem {problem}"
        )
        await ctx.send("Message sent.")

    @commands.command()
    @commands.check(lambda ctx: isinstance(ctx.channel, discord.DMChannel))
    async def mail(self, ctx, *, message):
        """Submit miscellaneous mail.
        Works in DMs only.
        """
        heading = f"Message from {ctx.author} (`{ctx.author.id}`)."
        channel = self.bot.get_channel(MAILBOX)
        if channel is None:
            return await ctx.send("Oops, I can't find the mailbox")

        await self.send_embed(
            channel, discord.Color.from_rgb(200, 200, 200),
            heading, message, ctx.message.attachments
        )
        await ctx.send("Message sent.")


    @commands.command(hidden=True)
    @commands.check(lambda ctx: ctx.channel.id==MAILBOX)
    async def reply(self, ctx, user: discord.User, *, mail):
        """Reply to a user"""
        heading = "Message from the Mathematical Olympiads Server Staff Team"
        await self.send_embed(
            user, discord.Color.from_rgb(100, 200, 200),
            heading, mail, ctx.message.attachments
        )
        await ctx.send(f"Message sent to {user}")

    async def send_embed(self, dest, color, heading, message, files, text=''):
        embed = discord.Embed()
        embed.title = heading
        embed.description = message
        embed.color = color
        if files:
            embed.set_image(url=files[0].proxy_url)

        await dest.send(text, embed=embed)




def setup(bot):
    bot.add_cog(Mail(bot))
