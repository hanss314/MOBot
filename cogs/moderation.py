import datetime
import discord

from discord.ext import commands

LOGCHAN = 559964001724006400
NEWROLE = 563807131275493443
MOGUILD = 533153217119387658
JOINMES = 564580597352103943
JOINREC = 564272059610431508
JOINCHA = 533156814145978390
RECNAME = "check"
LOUNGID = 533153217119387660

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        try:
            with open('data/joined.txt', 'r') as joinfile:
                self.joined = set(map(int, filter(lambda x: x, joinfile.read().split('\n'))))
        except FileNotFoundError:
            self.joined = set()

    async def on_member_join(self, member):
        if member.guild.id != MOGUILD: return
        await member.add_roles(self.bot.get_guild(MOGUILD).get_role(NEWROLE))
        time_now = datetime.datetime.utcnow()
        msg = f':white_check_mark: {member.mention} (`{member}` User #{member.guild.member_count}) ' \
              f'user joined the server. \n'

        creation_time = member.created_at
        time_diff = time_now - creation_time
        if time_diff.total_seconds() / 3600 <= 24:
            msg += ':clock1: '

        msg += 'User\'s account was created at ' + creation_time.strftime("%m/%d/%Y %I:%M:%S %p")
        await self.send(msg)

    def save_joined(self):
        with open('data/joined.txt', 'w') as joinfile:
            joinfile.write('\n'.join(map(str, self.joined)))

    async def on_member_remove(self, member):
        if member.guild.id != MOGUILD: return
        msg = f':x: {member.mention} (`{member}`) left the server.'
        await self.send(msg)

        channel = self.bot.get_channel(JOINCHA)
        message = await channel.fetch_message(JOINMES)
        self.joined.discard(member.id)
        self.save_joined()
        try:
            await message.remove_reaction(message.reactions[0], member)
        except Exception as e:
            await self.send(e)

    async def on_member_update(self, before, after):
        if before.guild.id != MOGUILD: return
        if before.name != after.name:
            msg = f'User **{before}** changed their name to **{after}** ({after.mention})'
            if before.discriminator != after.discriminator:
                msg += '\n:repeat: *User\'s discriminator changed!*'

            await self.send(msg)

        elif before.discriminator != after.discriminator:
            msg = f':repeat: User **{before}** ({before.mention})\'s discrim changed from ' \
                  f'{before.discriminator} to {after.discriminator}'
            await self.send(msg)

    async def on_message_edit(self, old, message):
        if message.guild is None or message.guild.id != MOGUILD: return
        if message.author.bot: return
        channel = message.guild.get_channel(LOGCHAN)
        if old.content == message.content: return
        if message.channel.id == channel.id: return
        embed = discord.Embed(title=f'Message edited in #{message.channel.name}',
                              colour=0xff7f00,
                              description=message.content,
                              timestamp=old.created_at)
        if old.content:
            embed.add_field(name='Old content:', value=old.content[:1024])
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_message_delete(self, message):
        if message.guild is None or message.guild.id != MOGUILD: return
        if message.author.bot: return
        channel = message.guild.get_channel(LOGCHAN)
        if message.channel.id == channel.id: return
        embed = discord.Embed(title=f'Message deleted in #{message.channel.name}',
                              colour=0xff0000,
                              description=message.content,
                              timestamp=message.created_at)
        embed.set_author(name=message.author.name, icon_url=message.author.avatar_url_as(format='png'))
        await channel.send(embed=embed)

    async def on_raw_reaction_add(self, payload):
        if payload.message_id != JOINMES or payload.emoji.id != JOINREC: return
        guild = self.bot.get_guild(MOGUILD)
        user = guild.get_member(payload.user_id)
        if user is not None and payload.emoji:
            try:
                await user.remove_roles(guild.get_role(NEWROLE))
            except discord.HTTPException as e:
                print(e)

            if user.id not in self.joined:
                await self.bot.get_channel(LOUNGID).send(
                    f"Welcome to the Mathematical Olympiad Discord server {user.mention}! "
                    f"We hope you enjoy your time here :smile:"
                )
                self.joined.add(user.id)
                self.save_joined()


    async def on_raw_reaction_remove(self, payload):
        if payload.message_id != JOINMES or payload.emoji.id != JOINREC: return
        guild = self.bot.get_guild(MOGUILD)
        user = guild.get_member(payload.user_id)
        if user is not None and payload.emoji:
            try:
                await user.add_roles(guild.get_role(NEWROLE))
            except discord.HTTPException as e:
                print(e)

    async def send(self, message):
        channel = self.bot.get_channel(LOGCHAN)
        await channel.send(message)


def setup(bot):
    bot.add_cog(Moderation(bot))
