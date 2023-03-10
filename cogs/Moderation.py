import discord
from scripts.main import connectdb
from os import getenv
from discord.ext import commands

class Moderation(commands.Cog):
    """
    Command untuk moderasi server.
    """
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        description="Memberikan pelanggaran kepada pengguna. (Harus berada di server ini)"
        )
    @commands.has_permissions(kick_members = True)
    async def warn(self, ctx:commands.Context, member:commands.MemberConverter, *, reason = None):
        """
        Memberikan pelanggaran kepada pengguna.
        """
        if ctx.author == member:
            return await ctx.reply("Kamu tidak bisa memberikan pelanggaran kepada dirimu!")
        if member.bot:
            return await ctx.reply("Uh... sepertinya memberikan pelanggaran kepada bot itu kurang berguna.")
        db = connectdb("Warns")
        reason = reason or "Tidak ada alasan dispesifikasi."
        warns = db.find_one({"_id":member.id})
        warnqty = 0 #Gee
        if warns is None:
            db.insert_one({"_id":member.id, "warns":1, "reason":[reason]})
            warnqty = 1
        else:
            db.update_one({"_id":member.id}, {'$inc':{"warns":1}, '$push':{"reason":reason}})
            warnqty = warns['warns']+1
        em = discord.Embed(title=f"Pelanggaran ❗", description = f"{member.mention} telah diberikan pelanggaran.\nDia sekarang telah diberikan **`{warnqty}`** pelanggaran.",
        color = member.colour
        )
        em.add_field(name="Reason", value=reason, inline=False)
        em.set_thumbnail(url = member.avatar.url if not member.avatar.url is None else getenv('normalpfp'))
        em.set_footer(text=f"Pelanggaran diberikan oleh {ctx.author} | ID:{ctx.author.id}", icon_url=ctx.author.avatar.url)
        await ctx.reply(embed = em)

    @commands.command(
        aliases=['wnhistory'], 
        description="Lihat riwayat pelanggaran pengguna di server ini.",
    )
    @commands.has_permissions(kick_members = True)
    async def warnhistory(self, ctx, member:commands.MemberConverter = None):
            """Lihat riwayat pelanggaran pengguna."""
            member = member or ctx.author
            db = connectdb("Warns")
            doc = db.find_one({'_id':member.id})
            if doc is None:
                return await ctx.reply(f"**`{member}`** saat ini belum memiliki pelanggaran.")
            reasons = doc['reason']
            emb = discord.Embed(title = f"Riwayat pelanggaran {member}", color = member.colour)
            emb.add_field(name= "Jumlah Pelanggaran", value=doc['warns'], inline=False)
            if doc['warns'] > 1:
                emb.add_field(name=f"Alasan (dari pelanggaran #1 to #{doc['warns']})", value="*"+"\n".join(reasons)+"*")
            else:
                emb.add_field(name=f"Reason", value="*"+"\n".join(reasons)+"*")
            emb.set_thumbnail(url = member.avatar.url if not member.avatar.url is None else getenv('normalpfp'))
            await ctx.reply(embed = emb)

    @commands.command(aliases=["rmwarn"], description="Menghilangkan segala data pelanggaran pengguna.")
    @commands.has_permissions(kick_members=True)
    async def removewarn(self, ctx, member:commands.MemberConverter):
        """
        Menghilangkan segala data pelanggaran pengguna.
        """
        db = connectdb("Warns")
        doc = db.find_one({"_id":member.id})
        if doc is None:
            return await ctx.reply(f"`{member}` belum pernah diberikan pelanggaran!")
        db.find_one_and_delete({"_id":member.id})
        await ctx.reply(f"Semua pelanggaran untuk {member.mention} telah dihapus.")

    """@commands.command(aliases=['wnlist'])
    @commands.has_permissions(ban_members=True)
    async def warnlist(self, ctx):
        db = connectdb('Warns')
        docs = db.find({})
        print(docs)""" #Unused for the moment.

    @commands.command(description="Ban pengguna dari server, walaupun dia di luar server ini.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx:commands.Context, user:commands.UserConverter, *, reason = None):
        """
        Ban pengguna dari server
        """
        reason = reason or "Tidak ada alasan dispesifikasi."
        await ctx.guild.ban(user)
        embed = discord.Embed(title="Ban ❗", color = ctx.author.colour)
        embed.description = f"**`{user}`** telah diban!"
        embed.add_field(name = "Alasan", value = reason, inline = False)
        embed.set_thumbnail(url = user.avatar.url if not user.avatar.url is None else getenv('normalpfp'))
        embed.set_footer(text=f"Dieksekusi oleh {ctx.author} | ID:{ctx.author.id}", icon_url=ctx.author.avatar.url)
        await ctx.reply(embed = embed)

    @commands.command(description="Unban seseorang yang telah diban sebelumnya.")
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: commands.UserConverter):
        """
        Unban pengguna yang telah diban.
        """
        try:
            await ctx.guild.unban(user)
            await ctx.send(f"{user} telah diunban.")
            return
        except:
            await ctx.send(f"Aku tidak bisa menemukan {user} di ban list!")
            return

    @commands.command(aliases = ['clean', 'purge', 'delete', 'hapus'], 
                      description="Menghilangkan pesan berdasarkan jumlah yang diinginkan (amount -> integer), (channel : opsional)")
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx:commands.Context, amount:int, channel:commands.TextChannelConverter = None):
        """
        Menghilangkan pesan berdasarkan jumlah yang diinginkan.
        """
        channel = channel or ctx.channel
        if amount <= 0:
            return await ctx.reply("Aku tidak bisa menghapus `0` pesan!")
        amount = amount or 5
        await channel.purge(limit = amount+1 if channel == ctx.channel else amount)
        await ctx.send(f"Aku telah menghapus {amount} pesan dari {channel.mention}.", delete_after = 5.0)

async def setup(bot):
    await bot.add_cog(Moderation(bot))